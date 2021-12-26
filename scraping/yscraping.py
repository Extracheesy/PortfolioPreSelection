import os
import re
from selenium import webdriver
import pandas as pd
import numpy as np

from yahoo_fin import stock_info as si

import config

def drop_df_duplicates(df):
    len_df = len(df)
    print("ticker nb: ", len_df)
    # dropping ALL duplicate values
    df.drop_duplicates(["symbol"], keep='first',inplace=True)
    print("duplicates removed:", len_df - len(df))
    return df

def set_df_index(df_tic, df_idx):
    df_tic.insert(len(df_tic.columns), "idx", "")
    for tic in df_tic["symbol"].tolist():
        try:
            tic_index = df_idx[df_idx['symbol'] == tic]['idx'].values[0]
        except:
            tic_index = "-"
        df_tic['idx'] = np.where(df_tic['symbol'] == tic, tic_index, df_tic['idx'])

    return df_tic

def get_list_index_stickers(driver):
    # NYSE
    driver.get('https://finance.yahoo.com/quote/%5ENYA/components')
    html_src_1 = driver.page_source

    html_src_str_1 = str(html_src_1)
    html_src_str_1 = html_src_str_1.replace("{",'\n')
    html_src_str_1 = html_src_str_1.replace("}",'\n')

    #match_1 = re.findall(r'components":[".*"],"maxAge', html_src_str_1)
    match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

    tmp_string = match_1[0][13:]
    size = len(tmp_string)
    string = tmp_string[: size - 9]
    list_nyse = string.split(",")

    for i in range(len(list_nyse)):
        list_nyse[i] = list_nyse[i][1:]
        list_nyse[i] = list_nyse[i][:-1]

    # CAC
    df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
    df_cac = df_html[3]
    list_cac = df_cac["Ticker"].tolist()

    # DAX
    df_html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
    df_dax = df_html[3]
    list_dax = df_dax["Ticker symbol"].tolist()

    return list_nyse, list_cac, list_dax

def get_stock_index_list(driver):
    list_nyse, list_cac, list_dax = get_list_index_stickers(driver)
    df_nyse = pd.DataFrame({'symbol': list_nyse})
    df_nyse.insert(len(df_nyse.columns), "idx", "^NYA")

    df_cac = pd.DataFrame({'symbol': list_cac})
    df_cac.insert(len(df_cac.columns), "idx", "^FCHI")

    df_dax = pd.DataFrame({'symbol': list_dax})
    df_dax.insert(len(df_dax.columns), "idx", "^GDAXI")

    list_dow = si.tickers_dow()
    df_dow = pd.DataFrame({'symbol': list_dow})
    df_dow.insert(len(df_dow.columns), "idx", "^DJI")

    list_nasdaq = si.tickers_nasdaq()
    df_nasdaq = pd.DataFrame({'symbol': list_nasdaq})
    df_nasdaq.insert(len(df_nasdaq.columns), "idx", "^IXIC")

    list_sp500 = si.tickers_sp500()
    df_sp500 = pd.DataFrame({'symbol': list_sp500})
    df_sp500.insert(len(df_sp500.columns), "idx", "^GSPC")

    df_result = df_sp500.append(df_cac)
    df_result = df_result.append(df_dax)
    df_result = df_result.append(df_dow)
    df_result = df_result.append(df_nasdaq)
    df_result = df_result.append(df_nyse)

    df_result.drop_duplicates(["symbol"], keep='first', inplace=True)

    return df_result

def get_info_list(list_stocks):
    list_sectors = []
    list_industry = []
    list_company_name = []
    for stock in list_stocks:
        try:
            info = si.get_company_info(stock)
            list_sectors.append(info['Value']['sector'])
            list_industry.append(info['Value']['industry'])
            # quote_table = si.get_quote_table(stock, dict_result=False)
            quote_data = si.get_quote_data(stock)

            try:
                stock_name = quote_data['shortName']
            except:
                try:
                    stock_name = quote_data['longName']
                except:
                    stock_name = stock
            list_company_name.append(stock_name)
        except:
            try:
                yf_stock = yf.Ticker(stock)
                industry = yf_stock.info['industry']
                sector = yf_stock.info['sector']
                shortName = yf_stock.info['shortName']

                list_sectors.append(sector)
                list_industry.append(industry)
                list_company_name.append(shortName)
            except:
                list_sectors.append('-')
                list_industry.append('-')
                list_company_name.append('-')

    return list_company_name, list_sectors, list_industry

def make_df_stock_info(list_stock, list_company_name, list_sectors, list_industry):
    return(pd.DataFrame({'symbol': list_stock,
                         'name': list_company_name,
                         'sector': list_sectors,
                         'industry': list_industry}))


def get_list_gainers(driver):
    if config.NO_SCRAPING == True:
        df_day_gainers = si.get_day_gainers()
        list_gainers = df_day_gainers['Symbol'].tolist()
        list_company_name, list_sectors, list_industry = get_info_list(list_gainers)

        return list_gainers, list_company_name, list_sectors, list_industry
    else:
        driver.get('https://finance.yahoo.com/gainers?offset=0&count=100')
        html_src_1 = driver.page_source
        driver.get('https://finance.yahoo.com/gainers?count=100&offset=100')
        html_src_2 = driver.page_source

        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{",'\n')
        html_src_str_1 = html_src_str_1.replace("}",'\n')

        html_src_str_2 = str(html_src_2)
        html_src_str_2 = html_src_str_2.replace("{",'\n')
        html_src_str_2 = html_src_str_2.replace("}",'\n')

        match_1 = re.findall(r'"symbol":".*","shortName":', html_src_str_1)
        match_2 = re.findall(r'"symbol":".*","shortName":', html_src_str_2)

        list_gainers = []

        for i in range(0,len(match_1),1):
            tmp_string = match_1[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_gainers.append(string)

        for i in range(0,len(match_2),1):
            tmp_string = match_2[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_gainers.append(string)

    return list_gainers

def get_list_DJI(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    df_dji = df_html[1]
    list_dji = df_dji["Symbol"].tolist()
    list_industry = df_dji["Industry"].tolist()
    list_company_name = df_dji["Company"].tolist()

    list_sectors = []
    for stock in list_dji:
        try:
            info = si.get_company_info(stock)
            list_sectors.append(info['Value']['sector'])
        except:
            try:
                yf_stock = yf.Ticker(stock)
                sector = yf_stock.info['sector']
                list_sectors.append(sector)
            except:
                list_sectors.append('-')

    return list_dji, list_company_name, list_sectors, list_industry

def get_list_SP500(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df_sp500 = df_html[0]
    list_sp500 = df_sp500["Symbol"].to_list()
    list_sectors = df_sp500["GICS Sector"].tolist()
    list_industry = df_sp500["GICS Sub-Industry"].tolist()
    list_company_name = df_sp500["Security"].tolist()

    return list_sp500, list_company_name, list_sectors, list_industry


def get_list_CAC(driver):
    if (config.WIKI == True):
        df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
        df_cac = df_html[3]
        list_cac = df_cac["Ticker"].tolist()
        list_sectors = df_cac["Sector"].tolist()
        list_industry = df_cac["GICS Sub-Industry"].tolist()
        list_company_name = df_cac["Company"].tolist()
    else:
        driver.get('https://fr.finance.yahoo.com/quote/%5EFCHI/components/')
        html_src_1 = driver.page_source

        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{",'\n')
        html_src_str_1 = html_src_str_1.replace("}",'\n')

        #match_1 = re.findall(r'components":[".*"],"maxAge', html_src_str_1)
        match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

        tmp_string = match_1[0][13:]
        size = len(tmp_string)
        string = tmp_string[: size - 9]
        list_cac = string.split(",")

        for i in range(len(list_cac)):
            list_cac[i] = list_cac[i][1:]
            list_cac[i] = list_cac[i][:-1]

    return list_cac, list_company_name, list_sectors, list_industry


def get_list_NYSE(driver):

    driver.get('https://finance.yahoo.com/quote/%5ENYA/components')
    html_src_1 = driver.page_source

    html_src_str_1 = str(html_src_1)
    html_src_str_1 = html_src_str_1.replace("{",'\n')
    html_src_str_1 = html_src_str_1.replace("}",'\n')

    #match_1 = re.findall(r'components":[".*"],"maxAge', html_src_str_1)
    match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

    tmp_string = match_1[0][13:]
    size = len(tmp_string)
    string = tmp_string[: size - 9]
    list_nyse = string.split(",")

    for i in range(len(list_nyse)):
        list_nyse[i] = list_nyse[i][1:]
        list_nyse[i] = list_nyse[i][:-1]

    list_company_name, list_sectors, list_industry = get_info_list(list_nyse)

    return list_nyse, list_company_name, list_sectors, list_industry

def get_list_DAX(driver):

    if (config.WIKI == True):
        df_html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
        df_dax = df_html[3]
        list_dax = df_dax["Ticker symbol"].tolist()
        list_sectors = df_dax["Prime Standard Sector"].tolist()
        # WARNING INDUSTRY INFO NOT IN WIKI - TO BE IMPLEMENTED LATER
        list_industry = df_dax["Prime Standard Sector"].tolist()
        list_company_name = df_dax["Company"].tolist()
    else:
        driver.get('https://finance.yahoo.com/quote/%5EGDAXI/components?p=%5EGDAXI')
        html_src_1 = driver.page_source
        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{",'\n')
        html_src_str_1 = html_src_str_1.replace("}",'\n')
        match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)
        tmp_string = match_1[0][13:]
        size = len(tmp_string)
        string = tmp_string[: size - 9]
        list_dax = string.split(",")
        for i in range(len(list_dax)):
            list_dax[i] = list_dax[i][1:]
            list_dax[i] = list_dax[i][:-1]

        list_company_name, list_sectors, list_industry = get_info_list(list_dax)

    return list_dax, list_company_name, list_sectors, list_industry


def get_NASDAQ_ticker_list():

    # list all NASDAQ stocks
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")

    df = df[(df['Test Issue'] == "N")]

    return df

def get_list_NASDAQ(driver):
    if (config.NO_SCRAPING == True) and (config.NASDAQ_100 == False):
        list_nasdaq = si.tickers_nasdaq()
        list_company_name, list_sectors, list_industry = get_info_list(list_nasdaq)

        return list_nasdaq, list_company_name, list_sectors, list_industry
    else:
        if (config.NASDAQ_100 == True):
            df_html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
            df_NASDAQ = df_html[3]
            list_nasdaq= df_NASDAQ["Ticker"].tolist()
            list_sectors = df_NASDAQ["GICS Sector"].tolist()
            list_industry = df_NASDAQ["GICS Sub-Industry"].tolist()
            list_company_name = df_NASDAQ["Company"].tolist()

            return list_nasdaq, list_company_name, list_sectors, list_industry
        else:
            # CODE NO USED
            if (config.NASDAQ_SCRAPING == True):
                driver.get('https://finance.yahoo.com/quote/%5EIXIC/components?p=%5EIXIC')
                html_src_1 = driver.page_source

                html_src_str_1 = str(html_src_1)
                html_src_str_1 = html_src_str_1.replace("{",'\n')
                html_src_str_1 = html_src_str_1.replace("}",'\n')

                #match_1 = re.findall(r'components":[".*"],"maxAge', html_src_str_1)
                match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

                tmp_string = match_1[0][13:]
                size = len(tmp_string)
                string = tmp_string[: size - 9]
                list_NASDAQ = string.split(",")

                for i in range(len(list_NASDAQ)):
                    list_NASDAQ[i] = list_NASDAQ[i][1:]
                    list_NASDAQ[i] = list_NASDAQ[i][:-1]
            else:
                df_NASDAQ_ticker_list = get_NASDAQ_ticker_list()
                list_NASDAQ = df_NASDAQ_ticker_list["Symbol"]

        return list_NASDAQ

def get_list_losers(driver):
    if config.NO_SCRAPING == True:
        df_day_losers = si.get_day_losers()
        list_losers = df_day_losers['Symbol'].tolist()
        list_company_name, list_sectors, list_industry = get_info_list(list_losers)

        return list_losers, list_company_name, list_sectors, list_industry
    else:
        # DEAD CODE
        driver.get('https://finance.yahoo.com/losers?offset=0&count=100')
        html_src_1 = driver.page_source
        driver.get('https://finance.yahoo.com/losers?count=100&offset=100')
        html_src_2 = driver.page_source

        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{",'\n')
        html_src_str_1 = html_src_str_1.replace("}",'\n')

        html_src_str_2 = str(html_src_2)
        html_src_str_2 = html_src_str_2.replace("{",'\n')
        html_src_str_2 = html_src_str_2.replace("}",'\n')

        match_1 = re.findall(r'"symbol":".*","shortName":', html_src_str_1)
        match_2 = re.findall(r'"symbol":".*","shortName":', html_src_str_2)

        list_losers = []

        for i in range(0, len(match_1), 1):
            tmp_string = match_1[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_losers.append(string)

        for i in range(0, len(match_2), 1):
            tmp_string = match_2[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_losers.append(string)

    return list_losers, list_company_name, list_sectors, list_industry

def get_list_trending_tickers(driver):
    driver.get('https://finance.yahoo.com/trending-tickers')
    html_src_1 = driver.page_source

    html_src_str_1 = str(html_src_1)
    html_src_str_1 = html_src_str_1.replace("{",'\n')
    html_src_str_1 = html_src_str_1.replace("}",'\n')

    match_1 = re.findall(r'"YFINANCE:.*","fallbackCategory":', html_src_str_1)
    tmp_string = match_1[0][10:]
    size = len(tmp_string)
    string = tmp_string[: size - 21]
    list_trending_tickers = string.split(",")
    list_company_name, list_sectors, list_industry = get_info_list(list_trending_tickers)

    return list_trending_tickers, list_company_name, list_sectors, list_industry

def get_list_most_actives(driver):
    if config.NO_SCRAPING == True:
        df_day_losers = si.get_day_most_active()
        list_most_actives = df_day_losers['Symbol'].tolist()
    else:
        driver.get('https://finance.yahoo.com/most-active?offset=0&count=100')
        html_src_1 = driver.page_source
        driver.get('https://finance.yahoo.com/most-active?count=100&offset=100')
        html_src_2 = driver.page_source

        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{", '\n')
        html_src_str_1 = html_src_str_1.replace("}", '\n')

        html_src_str_2 = str(html_src_2)
        html_src_str_2 = html_src_str_2.replace("{", '\n')
        html_src_str_2 = html_src_str_2.replace("}", '\n')

        match_1 = re.findall(r'"symbol":".*","shortName":', html_src_str_1)
        match_2 = re.findall(r'"symbol":".*","shortName":', html_src_str_2)

        list_most_actives = []
        for i in range(0, len(match_1), 1):
            tmp_string = match_1[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_most_actives.append(string)

        for i in range(0, len(match_2), 1):
            tmp_string = match_2[i][10:]
            size = len(tmp_string)
            string = tmp_string[: size - 14]
            list_most_actives.append(string)

    list_company_name, list_sectors, list_industry = get_info_list(list_most_actives)

    return list_most_actives, list_company_name, list_sectors, list_industry

def clean_up_df_symbol(df_ticker):
    toto = len(df_ticker)
    print("ticker nb: ",len(df_ticker))
    df_ticker = df_ticker.sort_values(by='Symbol')
    #df_ticker = df_ticker.drop_duplicates()
    df_ticker = df_ticker[~df_ticker.Symbol.str.contains(r'\\')]

    df_list_to_remove = pd.read_csv("./data/ticker_out_of_use.csv")

    for tic in df_list_to_remove["Symbol"]:
        #df_ticker = df_ticker[~df_ticker.Symbol.str.contains(str(tic))]
        df_ticker = df_ticker[df_ticker['Symbol'] != str(tic)]

    print("ticker removed: ", toto - len(df_ticker))
    return df_ticker

def get_YAHOO_ticker_list():
    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    if config.READ_LIST_FROM_PREVIOUS_CSV == True:
        df_ticker = pd.read_csv(config.OUTPUT_DIR+"dump_stock_info.csv")
    else:
        if (config.COLAB == True):
            options = webdriver.ChromeOptions()
            options.add_argument('-headless')
            options.add_argument('-no-sandbox')
            options.add_argument('-disable-dev-shm-usage')
            driver = webdriver.Chrome('chromedriver', options=options)
        else:
            #DRIVER_PATH = "C:/Users/despo/chromedriver_win32/chromedriver.exe"
            DRIVER_PATH = "./chromedriver.exe"
            options = webdriver.ChromeOptions()
            options.add_argument('-headless')
            options.headless = True
            options.add_argument('-no-sandbox')
            options.add_argument('-window-size=1920,1200')
            options.add_argument('-disable-gpu')
            options.add_argument('-ignore-certificate-errors')
            options.add_argument('-disable-extensions')
            options.add_argument('-disable-dev-shm-usage')
            #driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
            driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)

        driver.get('https://finance.yahoo.com/gainers')

        if (config.COLAB == False):
            driver.find_element_by_name("agree").click()

        list_DAX, list_company_name, list_sectors, list_industry = get_list_DAX(driver)
        df_DAX = make_df_stock_info(list_DAX, list_company_name, list_sectors, list_industry)
        df_DAX.insert(len(df_DAX.columns), "Type", "-")

        list_SP500, list_company_name, list_sectors, list_industry = get_list_SP500(driver)
        df_SP500 = make_df_stock_info(list_SP500, list_company_name, list_sectors, list_industry)
        df_SP500.insert(len(df_SP500.columns), "Type", "-")

        list_CAC, list_company_name, list_sectors, list_industry = get_list_CAC(driver)
        df_CAC = make_df_stock_info(list_CAC, list_company_name, list_sectors, list_industry)
        df_CAC.insert(len(df_CAC.columns), "Type", "-")

        list_DJI, list_company_name, list_sectors, list_industry = get_list_DJI(driver)
        df_DJI = make_df_stock_info(list_DJI, list_company_name, list_sectors, list_industry)
        df_DJI.insert(len(df_DJI.columns), "Type", "-")

        list_most_actives, list_company_name, list_sectors, list_industry = get_list_most_actives(driver)
        df_actives = make_df_stock_info(list_most_actives, list_company_name, list_sectors, list_industry)
        df_actives.insert(len(df_actives.columns), "Type", "ACTIVES")

        list_trending_tickers, list_company_name, list_sectors, list_industry = get_list_trending_tickers(driver)
        df_trending = make_df_stock_info(list_trending_tickers, list_company_name, list_sectors, list_industry)
        df_trending.insert(len(df_trending.columns), "Type", "TRENDING")

        list_NASDAQ, list_NASDQ_company_name, list_NASDQ_sectors, list_NASDQ_industry = get_list_NASDAQ(driver)
        df_NASDAQ = make_df_stock_info(list_NASDAQ, list_NASDQ_company_name, list_NASDQ_sectors, list_NASDQ_industry)
        df_NASDAQ.insert(len(df_NASDAQ.columns), "Type", "-")

        list_gainers, list_company_name, list_sectors, list_industry = get_list_gainers(driver)
        df_gainers = make_df_stock_info(list_gainers, list_company_name, list_sectors, list_industry)
        df_gainers.insert(len(df_gainers.columns), "Type", "GAINERS")

        list_losers, list_company_name, list_sectors, list_industry = get_list_losers(driver)
        df_loosers = make_df_stock_info(list_losers, list_company_name, list_sectors, list_industry)
        df_loosers.insert(len(df_loosers.columns), "Type", "LOOSERS")

        # NYSE nb Stokes > 4000
        if config.GET_NYSE == True:
            list_NYSE, list_company_name, list_sectors, list_industry = get_list_NYSE(driver)
            df_NYSE = make_df_stock_info(list_NYSE, list_company_name, list_sectors, list_industry)
            df_NYSE.insert(len(df_NYSE.columns), "Type", "-")


        df_ticker = pd.DataFrame()
        df_ticker = df_ticker.append(df_gainers, ignore_index=True)
        df_ticker = df_ticker.append(df_actives, ignore_index=True)
        df_ticker = df_ticker.append(df_trending, ignore_index=True)
        df_ticker = df_ticker.append(df_loosers, ignore_index=True)
        df_ticker = df_ticker.append(df_CAC, ignore_index=True)
        df_ticker = df_ticker.append(df_NASDAQ, ignore_index=True)
        df_ticker = df_ticker.append(df_DAX, ignore_index=True)
        df_ticker = df_ticker.append(df_DJI, ignore_index=True)
        df_ticker = df_ticker.append(df_SP500, ignore_index=True)
        if config.GET_NYSE == True:
            df_ticker = df_ticker.append(df_NYSE, ignore_index=True)

        # df_ticker.to_csv(config.DIR + "before_dump_stock_info.csv")

        df_ticker = drop_df_duplicates(df_ticker)

        #df_ticker = clean_up_df_symbol(df_ticker)

        df_all_index = get_stock_index_list(driver)
        df_ticker = set_df_index(df_ticker, df_all_index)

        df_ticker.sort_values(by='symbol', inplace=True, ascending=True)
        df_ticker = df_ticker.reset_index()
        # df_ticker = df_ticker.drop(['index'], axis=1)

        print("dump info to dump_stock_info.csv")
        df_ticker.to_csv(config.OUTPUT_DIR+"dump_stock_info.csv")

    return df_ticker