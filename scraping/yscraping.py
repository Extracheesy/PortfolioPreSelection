import os
import re
from selenium import webdriver
import pandas as pd

def get_list_gainers(driver):

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
    list_dji = df_dji["Symbol"]

    return list_dji

def get_list_SP500(driver):
    WIKI = True

    if WIKI == True:
        df_html = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df_sp500 = df_html[0]
        list_sp500 = df_sp500["Symbol"]

        return list_sp500
    else:
        url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/master/data/constituents.csv'
        df = pd.read_csv(url)

        return df["Symbol"]

def get_list_CAC(driver):
    YAHOO = False

    if (YAHOO == True):
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
    else:

        df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
        df_cac = df_html[3]
        list_cac = df_cac["Ticker"]

    return list_cac

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

    return list_nyse

def get_list_DAX(driver):
    YAHOO = False

    if (YAHOO == True):
        driver.get('https://finance.yahoo.com/quote/%5EGDAXI/components?p=%5EGDAXI')
        html_src_1 = driver.page_source

        html_src_str_1 = str(html_src_1)
        html_src_str_1 = html_src_str_1.replace("{",'\n')
        html_src_str_1 = html_src_str_1.replace("}",'\n')

        #match_1 = re.findall(r'components":[".*"],"maxAge', html_src_str_1)
        match_1 = re.findall(r'components":.*,"maxAge', html_src_str_1)

        tmp_string = match_1[0][13:]
        size = len(tmp_string)
        string = tmp_string[: size - 9]
        list_dax = string.split(",")

        for i in range(len(list_dax)):
            list_dax[i] = list_dax[i][1:]
            list_dax[i] = list_dax[i][:-1]
    else:
        df_html = pd.read_html('https://en.wikipedia.org/wiki/CAC_40')
        df_dax = df_html[3]
        list_dax = df_dax["Ticker"]

    return list_dax

def get_NASDAQ_ticker_list():

    # list all NASDAQ stocks
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")

    df = df[(df['Test Issue'] == "N")]

    return df

def get_list_NASDAQ(driver):

    SCRAPING = "OFF"
    NASDAQ_100 = True

    if NASDAQ_100 == True:
        df_html = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
        df_NASDAQ = df_html[3]
        list_NASDAQ= df_NASDAQ["Ticker"]

    else:
        if (SCRAPING == "ON"):
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

    return list_losers

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

    return list_trending_tickers

def get_list_most_actives(driver):

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

    return list_most_actives

def clean_up_df_symbol(df_ticker):
    toto = len(df_ticker)
    print("ticker nb: ",len(df_ticker))
    #df_ticker = df_ticker.drop_duplicates()
    df_ticker = df_ticker[~df_ticker.Symbol.str.contains(r'\\')]

    df_list_to_remove = pd.read_csv("./data/ticker_out_of_use.csv")

    for tic in df_list_to_remove["Symbol"]:
        #df_ticker = df_ticker[~df_ticker.Symbol.str.contains(str(tic))]
        df_ticker = df_ticker[df_ticker['Symbol'] != str(tic)]

    print("ticker removed: ", toto - len(df_ticker))
    return df_ticker

def get_YAHOO_ticker_list():

    ENV_MODE = "PC"

    if (ENV_MODE == "PC"):
        DRIVER_PATH = "C:/Users/despo/chromedriver_win32/chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        options.add_argument('-no-sandbox')
        options.add_argument('-window-size=1920,1200')
        options.add_argument('-disable-gpu')
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('-disable-extensions')
        options.add_argument('-disable-dev-shm-usage')
        #driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    if (ENV_MODE == "COLAB"):
        options = webdriver.ChromeOptions()
        options.add_argument('-headless')
        options.add_argument('-no-sandbox')
        options.add_argument('-disable-dev-shm-usage')
        driver = webdriver.Chrome('chromedriver', options=options)

    driver.get('https://finance.yahoo.com/gainers')

    if (ENV_MODE == "PC"):
        driver.find_element_by_name("agree").click()

    list_gainers = get_list_gainers(driver)
    df_gainers = pd.DataFrame({'Symbol': list_gainers})
    df_gainers.insert(len(df_gainers.columns), "Type", "GAINERS")

    list_losers = get_list_losers(driver)
    df_loosers = pd.DataFrame({'Symbol': list_losers})
    df_loosers.insert(len(df_loosers.columns), "Type", "LOOSERS")

    list_trending_tickers = get_list_trending_tickers(driver)
    df_trending = pd.DataFrame({'Symbol': list_trending_tickers})
    df_trending.insert(len(df_trending.columns), "Type", "TRENDING")

    list_most_actives = get_list_most_actives(driver)
    df_actives = pd.DataFrame({'Symbol': list_most_actives})
    df_actives.insert(len(df_actives.columns), "Type", "ACTIVES")

    list_DAX = get_list_DAX(driver)
    df_DAX = pd.DataFrame({'Symbol': list_DAX})
    df_DAX.insert(len(df_DAX.columns), "Type", "DAX")

    list_DJI = get_list_DJI(driver)
    df_DJI = pd.DataFrame({'Symbol': list_DJI})
    df_DJI.insert(len(df_DJI.columns), "Type", "DJI")

    list_NASDAQ = get_list_NASDAQ(driver)
    df_NASDAQ = pd.DataFrame({'Symbol': list_NASDAQ})
    df_NASDAQ.insert(len(df_NASDAQ.columns), "Type", "NASDAQ")

    list_CAC = get_list_CAC(driver)
    df_CAC = pd.DataFrame({'Symbol': list_CAC})
    df_CAC.insert(len(df_CAC.columns), "Type", "CAC40")

    list_SP500 = get_list_SP500(driver)
    df_SP500 = pd.DataFrame({'Symbol': list_SP500})
    df_SP500.insert(len(df_SP500.columns), "Type", "SP500")

    #list_NYSE = get_list_NYSE(driver)
    #df_NYSE = pd.DataFrame({'Symbol': list_NYSE})
    #df_NYSE.insert(len(df_NYSE.columns), "Type", "NYSE")

    df_ticker = pd.DataFrame()
    df_ticker = df_ticker.append(df_gainers, ignore_index=True)
    df_ticker = df_ticker.append(df_loosers, ignore_index=True)
    df_ticker = df_ticker.append(df_trending, ignore_index=True)
    df_ticker = df_ticker.append(df_actives, ignore_index=True)
    df_ticker = df_ticker.append(df_CAC, ignore_index=True)
    df_ticker = df_ticker.append(df_NASDAQ, ignore_index=True)
    df_ticker = df_ticker.append(df_DAX, ignore_index=True)
    df_ticker = df_ticker.append(df_DJI, ignore_index=True)
    df_ticker = df_ticker.append(df_SP500, ignore_index=True)
    #df_ticker = df_ticker.append(df_NYSE, ignore_index=True)

    df_ticker = clean_up_df_symbol(df_ticker)

    df_ticker.sort_values(by='Symbol', inplace=True, ascending=True)
    df_ticker = df_ticker.reset_index()
    df_ticker = df_ticker.drop(['index'], axis=1)

    return df_ticker