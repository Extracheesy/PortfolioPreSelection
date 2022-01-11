import os
import re
from selenium import webdriver
import pandas as pd
import numpy as np
#import asyncio
import uuid
import datetime

import concurrent.futures

from yahoo_fin import stock_info as si
import yfinance as yf

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

    # CAC40
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

def get_df_info_list(list_stocks):
    list_tickers = []
    list_sectors = []
    list_industry = []
    list_company_name = []
    list_country = []
    list_exchange = []
    list_yahoo_recom_mean = []
    list_yahoo_recom_key = []
    for stock in list_stocks:
        get_data_success = True
        sector = '-'
        industry = ('-')
        company_name = ('-')
        country = ('-')
        exchange = ('-')
        yahoo_recom_key = ('-')
        yahoo_recom_mean = ('-')
        try:
            yf_stock = yf.Ticker(stock)
            industry = yf_stock.info['industry']
            sector = yf_stock.info['sector']
            company_name = yf_stock.info['shortName']
            country = yf_stock.info['country']
            exchange = yf_stock.info['exchange']
            yahoo_recom_key = yf_stock.info['recommendationKey']
            yahoo_recom_mean = yf_stock.info['recommendationMean']

            quote_data = si.get_quote_data(stock)
            exchange = quote_data['fullExchangeName']
            toto = '0'
        except:
            try:
                info = si.get_company_info(stock)
                sector = info['Value']['sector']
                industry = info['Value']['industry']
                country = info['Value']['country']
                quote_data = si.get_quote_data(stock)
                exchange = quote_data['fullExchangeName']
                yahoo_recommendation = quote_data['averageAnalystRating']
                yahoo_recommendation_split = yahoo_recommendation.split(" - ")
                yahoo_recom_mean = yahoo_recommendation_split[0]
                yahoo_recom_key = yahoo_recommendation_split[1]
                toto = '1'
                try:
                    company_name = quote_data['shortName']
                except:
                    try:
                        company_name = quote_data['longName']
                    except:
                        company_name = stock
            except:
                print('error yahoo data stock: ',stock)
                get_data_success = False
        if get_data_success == True:
            print('get yahoo data stock: ', stock,' -> ',toto)
            list_tickers.append(stock)
            list_sectors.append(sector)
            list_industry.append(industry)
            list_company_name.append(company_name)
            list_country.append(country)
            list_exchange.append(exchange)
            list_yahoo_recom_key.append(yahoo_recom_key)
            list_yahoo_recom_mean.append(yahoo_recom_mean)
        else:
            get_data_success = True

    df = make_df_stock_info(list_tickers, list_company_name,
                            list_sectors, list_industry,
                            list_country, list_exchange,
                            list_yahoo_recom_mean, list_yahoo_recom_key)

    return df

def get_multithreading_df_info_list(list_stocks):
    list_tickers = []
    list_sectors = []
    list_industry = []
    list_company_name = []
    list_country = []
    list_exchange = []
    list_yahoo_recom_mean = []
    list_yahoo_recom_key = []
    for stock in list_stocks:
        get_data_success = True
        sector = '-'
        industry = ('-')
        company_name = ('-')
        country = ('-')
        exchange = ('-')
        yahoo_recom_key = ('-')
        yahoo_recom_mean = ('-')
        try:
            yf_stock = yf.Ticker(stock)
            industry = yf_stock.info['industry']
            sector = yf_stock.info['sector']
            company_name = yf_stock.info['shortName']
            country = yf_stock.info['country']
            exchange = yf_stock.info['exchange']
            yahoo_recom_key = yf_stock.info['recommendationKey']
            yahoo_recom_mean = yf_stock.info['recommendationMean']

            quote_data = si.get_quote_data(stock)
            exchange = quote_data['fullExchangeName']
        except:
            print('error yahoo data stock: ',stock)
            get_data_success = False
        if get_data_success == True:
            print('get yahoo data stock: ', stock)
            list_tickers.append(stock)
            list_sectors.append(sector)
            list_industry.append(industry)
            list_company_name.append(company_name)
            list_country.append(country)
            list_exchange.append(exchange)
            list_yahoo_recom_key.append(yahoo_recom_key)
            list_yahoo_recom_mean.append(yahoo_recom_mean)
        else:
            get_data_success = True

    df = make_df_stock_info(list_tickers, list_company_name,
                            list_sectors, list_industry,
                            list_country, list_exchange,
                            list_yahoo_recom_mean, list_yahoo_recom_key)

    filename = config.OUTPUT_POOL_DIR + str(uuid.uuid4()) + '.csv'
    df.to_csv(filename)


def get_info_list(list_stocks):
    list_tickers = []
    list_sectors = []
    list_industry = []
    list_company_name = []
    list_country = []
    list_exchange = []
    list_yahoo_recom_mean = []
    list_yahoo_recom_key = []
    for stock in list_stocks:
        get_data_success = True
        sector = '-'
        industry = ('-')
        company_name = ('-')
        country = ('-')
        exchange = ('-')
        yahoo_recom_key = ('-')
        yahoo_recom_mean = ('-')
        try:
            yf_stock = yf.Ticker(stock)
            industry = yf_stock.info['industry']
            sector = yf_stock.info['sector']
            company_name = yf_stock.info['shortName']
            country = yf_stock.info['country']
            exchange = yf_stock.info['exchange']
            yahoo_recom_key = yf_stock.info['recommendationKey']
            yahoo_recom_mean = yf_stock.info['recommendationMean']

            quote_data = si.get_quote_data(stock)
            exchange = quote_data['fullExchangeName']
        except:
            try:
                info = si.get_company_info(stock)
                sector = info['Value']['sector']
                industry = info['Value']['industry']
                country = info['Value']['country']
                quote_data = si.get_quote_data(stock)
                exchange = quote_data['fullExchangeName']
                yahoo_recommendation = quote_data['averageAnalystRating']
                yahoo_recommendation_split = yahoo_recommendation.split(" - ")
                yahoo_recom_mean = yahoo_recommendation_split[0]
                yahoo_recom_key = yahoo_recommendation_split[1]
                try:
                    company_name = quote_data['shortName']
                except:
                    try:
                        company_name = quote_data['longName']
                    except:
                        company_name = stock
            except:
                print('error yahoo data stock: ',stock)
                get_data_success = False
        if get_data_success == True:
            print('get yahoo data stock: ', stock)
            list_tickers.append(stock)
            list_sectors.append(sector)
            list_industry.append(industry)
            list_company_name.append(company_name)
            list_country.append(country)
            list_exchange.append(exchange)
            list_yahoo_recom_key.append(yahoo_recom_key)
            list_yahoo_recom_mean.append(yahoo_recom_mean)
        else:
            get_data_success = True

    return list_tickers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def make_df_stock_info(list_stock, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key):
    return(pd.DataFrame({'symbol': list_stock,
                         'name': list_company_name,
                         'sector': list_sectors,
                         'industry': list_industry,
                         'country': list_country,
                         'exchange' : list_exchange,
                         'yahoo_recom_mean': list_yahoo_recom_mean,
                         'yahoo_recom_key': list_yahoo_recom_key}))


def get_list_gainers(driver):
    df_day_gainers = si.get_day_gainers()
    list_gainers = df_day_gainers['Symbol'].tolist()
    list_gainers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_gainers)

    return list_gainers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_list_DJI(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
    df_dji = df_html[1]
    list_dji = df_dji["Symbol"].tolist()
    #list_industry = df_dji["Industry"].tolist()
    #list_company_name = df_dji["Company"].tolist()

    list_dji, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_dji)

    return list_dji, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_list_SP500(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df_sp500 = df_html[0]
    list_sp500 = df_sp500["Symbol"].to_list()
    # list_sectors = df_sp500["GICS Sector"].tolist()
    # list_industry = df_sp500["GICS Sub-Industry"].tolist()
    # list_company_name = df_sp500["Security"].tolist()

    list_sp500, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_sp500)

    return list_sp500, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key


def get_list_CAC(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
    df_cac = df_html[3]
    list_cac = df_cac["Ticker"].tolist()
    # list_sectors = df_cac["Sector"].tolist()
    # list_industry = df_cac["GICS Sub-Industry"].tolist()
    # list_company_name = df_cac["Company"].tolist()

    list_cac, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_cac)

    return list_cac, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_list_NYSE(driver):
    driver.get('https://finance.yahoo.com/quote/%5ENYA/components')
    html_src_1 = driver.page_source

    html_src_str_1 = str(html_src_1)
    html_src_str_1 = html_src_str_1.replace("{",'\n')
    html_src_str_1 = html_src_str_1.replace("}",'\n')

    match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

    tmp_string = match_1[0][13:]
    size = len(tmp_string)
    string = tmp_string[: size - 9]
    list_nyse = string.split(",")

    for i in range(len(list_nyse)):
        list_nyse[i] = list_nyse[i][1:]
        list_nyse[i] = list_nyse[i][:-1]

    list_nyse, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_nyse)

    return list_nyse, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_list_DAX(driver):
    df_html = pd.read_html('https://en.wikipedia.org/wiki/DAX')
    df_dax = df_html[3]
    list_dax = df_dax["Ticker symbol"].tolist()
    # WARNING INDUSTRY INFO NOT IN WIKI - TO BE IMPLEMENTED LATER
    # list_industry = df_dax["Prime Standard Sector"].tolist()
    # list_company_name = df_dax["Company"].tolist()
    # list_sectors = df_dax["Prime Standard Sector"].tolist()

    list_dax, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_dax)

    return list_dax, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_NASDAQ_ticker_list():
    # list all NASDAQ stocks
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")

    df = df[(df['Test Issue'] == "N")]

    return df

def get_list_NASDAQ(driver):
    if config.NASDAQ_100 == False:
        list_nasdaq = si.tickers_nasdaq()
        list_nasdaq, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_nasdaq)
        return list_nasdaq, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key
    else:
        df_html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
        df_NASDAQ = df_html[3]
        list_nasdaq= df_NASDAQ["Ticker"].tolist()
        # list_sectors = df_NASDAQ["GICS Sector"].tolist()
        # list_industry = df_NASDAQ["GICS Sub-Industry"].tolist()
        # list_company_name = df_NASDAQ["Company"].tolist()

        list_nasdaq, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_nasdaq)
        return list_nasdaq, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key


def get_list_losers(driver):
    df_day_losers = si.get_day_losers()
    list_losers = df_day_losers['Symbol'].tolist()
    list_losers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_losers)
    return list_losers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key


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

    list_trending_tickers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_trending_tickers)
    return list_trending_tickers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key


def get_list_most_actives(driver):
    df_day_losers = si.get_day_most_active()
    list_most_actives = df_day_losers['Symbol'].tolist()

    list_most_actives, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_info_list(list_most_actives)
    return list_most_actives, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key

def get_global_ticker_list(driver):
    df_result = pd.DataFrame()
    try:
        list_sp500 = si.tickers_sp500()
        df_sp500 = pd.DataFrame({'symbol': list_sp500})
        df_result = df_result.append(df_sp500)
    except:
        print("no symbol sp500")
    try:
        list_dow = si.tickers_dow()
        df_dow = pd.DataFrame({'symbol': list_dow})
        df_result = df_result.append(df_dow)
    except:
        print("no symbol dji")
    try:
        list_nasdaq = si.tickers_nasdaq()
        df_nasdaq = pd.DataFrame({'symbol': list_nasdaq})
        df_result = df_result.append(df_nasdaq)
    except:
        print("no symbol nasdaq")
    try:
        list_ftse100 = si.tickers_ftse100()
        df_ftse100 = pd.DataFrame({'symbol': list_ftse100})
        df_result = df_result.append(df_ftse100)
    except:
        print("no symbol ftse100")
    try:
        list_ftse250 = si.tickers_ftse250()
        df_ftse250 = pd.DataFrame({'symbol': list_ftse250})
        df_result = df_result.append(df_ftse250)
    except:
        print("no symbol ftse250")
    try:
        list_ibovespa = si.tickers_ibovespa()
        df_ibovespa = pd.DataFrame({'symbol': list_ibovespa})
        df_result = df_result.append(df_ibovespa)
    except:
        print("no symbol ibovespa")
    try:
        list_nifty50 = si.tickers_nifty50()
        df_nifty50 = pd.DataFrame({'symbol': list_nifty50})
        df_result = df_result.append(df_nifty50)
    except:
        print("no symbol nifty50")
    try:
        list_niftybank = si.tickers_niftybank()
        df_niftybank = pd.DataFrame({'symbol': list_niftybank})
        df_result = df_result.append(df_niftybank)
    except:
        print("no symbol niftybank")
    try:
        list_other = si.tickers_other()
        df_other = pd.DataFrame({'symbol': list_other})
        df_result = df_result.append(df_other)
    except:
        print("no symbol other")

    try:
        list_gainers = si.get_day_gainers()
        df_gainers = pd.DataFrame({'symbol': list_gainers})
        df_result = df_result.append(df_gainers)
    except:
        print("no symbol gainers")

    try:
        list_active = si.get_day_most_active()
        df_active = pd.DataFrame({'symbol': list_active})
        df_result = df_result.append(df_active)
    except:
        print("no symbol most active")

    try:
        list_losers = si.get_day_losers()
        df_losers = pd.DataFrame({'symbol': list_losers})
        df_result = df_result.append(df_losers)
    except:
        print("no symbol losers")

    list_nyse, list_cac, list_dax = get_list_index_stickers(driver)
    df_nyse = pd.DataFrame({'symbol': list_nyse})
    df_result = df_result.append(df_nyse)
    df_cac = pd.DataFrame({'symbol': list_cac})
    df_result = df_result.append(df_cac)
    df_dax = pd.DataFrame({'symbol': list_dax})
    df_result = df_result.append(df_dax)

    df_result.drop_duplicates(["symbol"], keep='first', inplace=True)
    df_result.sort_values(by=['symbol'], inplace=True)

    print("dump info to ticker_global_stock_list.csv")
    df_result.to_csv(config.OUTPUT_DIR + "ticker_global_stock_list.csv")

    return df_result

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

def split_list(a_list, size_split):
    return a_list[:size_split], a_list[size_split:]

async def get_asyncio_df_info_list(call_list):
    df_result = asyncio.gather(*call_list)
    return df_result

def get_YAHOO_ticker_list():
    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    if config.READ_LIST_FROM_PREVIOUS_CSV == True:
        if config.TEST_GLOBAL == True:
            df_ticker = pd.read_csv(config.OUTPUT_DIR + "ticker_global_stock_info_list.csv")
        else:
            df_ticker = pd.read_csv(config.OUTPUT_DIR + "dump_stock_info.csv")
    else:
        if (config.COLAB == True):
            options = webdriver.ChromeOptions()
            options.add_argument('-headless')
            options.add_argument('-no-sandbox')
            options.add_argument('-disable-dev-shm-usage')
            driver = webdriver.Chrome('chromedriver', options=options)
        else:
            #DRIVER_PATH = "C:/Users/despo/chromedriver_win32/chromedriver.exe"
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
            driver = webdriver.Chrome(executable_path=config.DRIVER_PATH, options=options)

        driver.get('https://finance.yahoo.com/gainers')

        if (config.COLAB == False):
            driver.find_element_by_name("agree").click()

        if config.TEST_GLOBAL == True:
            if config.READ_GLOBAL_LIST_FROM_PREVIOUS_CSV == True:
                df_ticker = pd.read_csv(config.OUTPUT_DIR + "ticker_global_stock_list.csv")
                df_ticker.drop(df_ticker.filter(regex="Unnamed: 0"), axis=1, inplace=True)
                df_ticker.dropna(inplace=True)
                df_ticker.reset_index(inplace=True, drop=True)
            else:
                df_ticker = get_global_ticker_list(driver)

            list_symbol = df_ticker["symbol"].to_list()

            len_global_list_symbol = len(list_symbol)
            len_split_global_list_symbol = int(len_global_list_symbol / config.NB_SPLIT_LIST_SYMBOL)

            rest_of_the_list = list_symbol
            global_split_list = []
            for i in range(config.NB_SPLIT_LIST_SYMBOL):
                splited_list, rest_of_the_list = split_list(rest_of_the_list, len_split_global_list_symbol)
                global_split_list.append(splited_list)

            if len(rest_of_the_list) > 1:
                global_split_list.append(rest_of_the_list)

            call_list = []
            # for i in range(config.NB_SPLIT_LIST_SYMBOL):
            #    call_list.append(get_df_info_list(global_split_list[i]))

            if config.MULTITHREADING == True:
                print("MULTITHREADING START")
                START_TIME = datetime.datetime.now().now()
                with concurrent.futures.ThreadPoolExecutor(max_workers=config.NUM_THREADS) as executor:
                    executor.map(get_multithreading_df_info_list, global_split_list)
                print("MULTITHREADING RUNTIME: ", datetime.datetime.now().now() - START_TIME)
            elif config.ASYNCIO == True:
                print("ASYNCIO")
                # asyncio.run(get_asyncio_df_info_list(call_list))
                # this is the event loop
                loop = asyncio.get_event_loop()
                # schedule coroutines to run on the event loop
                loop.run_until_complete(asyncio.gather(call_list[2], call_list[3]))
            else:
                df_result = get_df_info_list(list_symbol)

            df_result.to_csv(config.OUTPUT_DIR + "ticker_global_stock_info_list.csv")

            return df_result
        else:
            list_SP500, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_SP500(driver)
            df_SP500 = make_df_stock_info(list_SP500, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_SP500.insert(len(df_SP500.columns), "Type", "SP500")
            print('list SP500 OK')
            list_DAX, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_DAX(driver)
            df_DAX = make_df_stock_info(list_DAX, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_DAX.insert(len(df_DAX.columns), "Type", "DAX")
            print('list DAX OK')
            list_CAC, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_CAC(driver)
            df_CAC = make_df_stock_info(list_CAC, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_CAC.insert(len(df_CAC.columns), "Type", "CAC40")
            print('list CAC OK')
            list_DJI, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_DJI(driver)
            df_DJI = make_df_stock_info(list_DJI, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_DJI.insert(len(df_DJI.columns), "Type", "DJI")
            print('list DJI OK')
            list_most_actives, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_most_actives(driver)
            df_actives = make_df_stock_info(list_most_actives, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_actives.insert(len(df_actives.columns), "Type", "ACTIVES")
            print('list MOST ACTIVES OK')
            list_trending_tickers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_trending_tickers(driver)
            df_trending = make_df_stock_info(list_trending_tickers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_trending.insert(len(df_trending.columns), "Type", "TRENDING")
            print('list TRENDING OK')
            list_NASDAQ, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_NASDAQ(driver)
            df_NASDAQ = make_df_stock_info(list_NASDAQ, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_NASDAQ.insert(len(df_NASDAQ.columns), "Type", "NASDAQ")
            print('list NASDAQ OK')
            list_gainers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_gainers(driver)
            df_gainers = make_df_stock_info(list_gainers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_gainers.insert(len(df_gainers.columns), "Type", "GAINERS")
            print('list GAINERS OK')
            list_losers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_losers(driver)
            df_loosers = make_df_stock_info(list_losers, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
            df_loosers.insert(len(df_loosers.columns), "Type", "LOOSERS")
            print('list LOOSERS OK')
            # NYSE nb Stokes > 4000
            if config.GET_NYSE == True:
                list_NYSE, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key = get_list_NYSE(driver)
                df_NYSE = make_df_stock_info(list_NYSE, list_company_name, list_sectors, list_industry, list_country, list_exchange, list_yahoo_recom_mean, list_yahoo_recom_key)
                df_NYSE.insert(len(df_NYSE.columns), "Type", "NYSE")
                print('list NYSE OK')

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
            df_all_index = get_stock_index_list(driver)
            df_ticker = set_df_index(df_ticker, df_all_index)

        df_ticker = drop_df_duplicates(df_ticker)

        #df_ticker = clean_up_df_symbol(df_ticker)

        df_ticker.sort_values(by='symbol', inplace=True, ascending=True)
        df_ticker = df_ticker.reset_index()
        # df_ticker = df_ticker.drop(['index'], axis=1)

        print("dump info to dump_stock_info.csv")
        df_ticker.to_csv(config.OUTPUT_DIR+"dump_stock_info.csv")

    return df_ticker