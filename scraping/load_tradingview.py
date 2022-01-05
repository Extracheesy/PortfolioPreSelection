# Imports
import time
import pandas as pd
import numpy as np
#from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver

import config

from bs4 import BeautifulSoup

from tradingview_ta import TA_Handler, Interval, Exchange

def insert_tradingview_df_column(df):
    columns = ["tradinview_symbol", "tradinview_country", "tradinview_index",
               "tradinview_recommandation", "tradinview_buy", "tradinview_sell", "tradinview_neutral"]
    for column in columns:
        df.insert(len(df.columns), column, "-")
    return df

def set_tradingview_data(df, symbol, data_handler, summary):
    #df['tradinview_index'] = np.where(df['tradinview_symbol'] == symbol, exchange, df['tradinview_index'])

    df.loc[symbol, 'tradinview_index'] = data_handler.exchange
    df.loc[symbol, 'tradinview_recommandation'] = summary['RECOMMENDATION']
    sum = summary['BUY'] + summary['SELL'] + summary['NEUTRAL']
    df.loc[symbol, 'tradinview_buy'] = int(summary['BUY'] / sum * 100)
    df.loc[symbol, 'tradinview_sell'] = int(summary['SELL'] / sum * 100)
    df.loc[symbol, 'tradinview_neutral'] = int(summary['NEUTRAL'] / sum * 100)

    return df


def set_tradingview_columns(df):

    # for idx_yahoo in config.INDEX:
    #    index_match = config.DF_MATCH_INDEX_FULLNAME.loc[idx_yahoo, 'index_tradingview']
    #    df['tradinview_index'] = np.where(df['idx'] == idx_yahoo, index_match, df['tradinview_index'])

    df['tradinview_index'] = df['exchange'].copy()
    df['tradinview_index'] = np.where(df['tradinview_index'] == 'XETRA', 'XETR', df['tradinview_index'])
    df['tradinview_index'] = np.where(df['tradinview_index'] == 'NasdaqGS', 'NASDQ', df['tradinview_index'])
    df['tradinview_index'] = np.where(df['tradinview_index'] == 'NasdaqCM', 'NASDQ', df['tradinview_index'])

    df['tradinview_index'] = np.where(df['tradinview_index'] == 'Paris', 'EURONEXT', df['tradinview_index'])


    df['tradinview_symbol'] = df['symbol'].copy()

    list_split_symbol = df['tradinview_symbol'].str.split("\\.", n=1, expand=True)
    df['tradinview_symbol'] = list_split_symbol[0]

    df['tradinview_country'] = df['country'].copy()
    df['tradinview_country'] = np.where(df['tradinview_country'] == 'United States', 'america', df['tradinview_country'])
    df['tradinview_country'] = np.where(df['tradinview_index'] == 'NYSE', 'america', df['tradinview_country'])

    # df['tradinview_country'] = np.where(df['tradinview_index'] == 'NASDAQ', 'america', df['tradinview_country'])

    # Cases:
    df['tradinview_country'] = np.where(df['tradinview_symbol'] == 'AIR', 'France', df['tradinview_country'])

    return df

def get_tradingview_signals(df_screener):

    df_screener = insert_tradingview_df_column(df_screener)
    df_screener = set_tradingview_columns(df_screener)

    # list_symbol = df_screener['tradinview_symbol'].tolist()
    # df_screener = df_screener.set_index('tradinview_symbol')
    list_symbol = df_screener['symbol'].tolist()
    df_screener = df_screener.set_index('symbol', drop=False)

    for symbol in list_symbol:
        ticker = symbol
        country = df_screener.loc[symbol, 'tradinview_country']
        exchange = df_screener.loc[symbol, 'tradinview_index']
        symbol = df_screener.loc[symbol, 'tradinview_symbol']
        data_handler_found = True
        if (country == 'america'):
            try:
                exchange = 'NYSE'
                data_handler = TA_Handler(
                    symbol=symbol,
                    screener=country,
                    exchange=exchange,
                    interval=Interval.INTERVAL_1_DAY,
                )
                # print("ticker: ", symbol, " exchange: ", exchange, " ",data_handler.get_analysis().summary)
                tradingview_summary = data_handler.get_analysis().summary
            except:
                try:
                    exchange = 'NASDAQ'
                    data_handler = TA_Handler(
                        symbol=symbol,
                        screener=country,
                        exchange=exchange,
                        interval=Interval.INTERVAL_1_DAY,
                    )
                    # print("ticker: ", symbol, " exchange: ", exchange, " ",data_handler.get_analysis().summary)
                    tradingview_summary = data_handler.get_analysis().summary
                except:
                    try:
                        exchange = 'AMEX'
                        data_handler = TA_Handler(
                            symbol=symbol,
                            screener=country,
                            exchange=exchange,
                            interval=Interval.INTERVAL_1_DAY,
                        )
                        # print("ticker: ", symbol, " exchange: ", exchange, " ",data_handler.get_analysis().summary)
                        tradingview_summary = data_handler.get_analysis().summary
                    except:
                        try:
                            exchange = 'SPX'
                            data_handler = TA_Handler(
                                symbol=symbol,
                                screener=country,
                                exchange=exchange,
                                interval=Interval.INTERVAL_1_DAY,
                            )
                            #print("ticker: ", symbol, " exchange: ", exchange, " ", data_handler.get_analysis().summary)
                            tradingview_summary = data_handler.get_analysis().summary
                        except:
                            data_handler_found = False
                            print("tradingview error ticker: ", symbol," country: ", country)
        else:
            try:
                data_handler = TA_Handler(
                    symbol=symbol,
                    screener=country,
                    exchange=exchange,
                    interval=Interval.INTERVAL_1_DAY,
                )
                # print("ticker: ", symbol, " exchange: ", exchange, " ",data_handler.get_analysis().summary)
                tradingview_summary = data_handler.get_analysis().summary
            except:
                try:
                    exchange = 'EURONEXT'
                    data_handler = TA_Handler(
                        symbol=symbol,
                        screener=country,
                        exchange=exchange,
                        interval=Interval.INTERVAL_1_DAY,
                    )
                    # print("ticker: ", symbol, " exchange: ", exchange, " ",data_handler.get_analysis().summary)
                    tradingview_summary = data_handler.get_analysis().summary
                except:
                    data_handler_found = False
                    print("tradingview error ticker: ", symbol," country: ", country)

        if data_handler_found == True:
            set_tradingview_data(df_screener, ticker, data_handler, tradingview_summary)

    df_screener.reset_index(inplace=True, drop=True)
    return df_screener
