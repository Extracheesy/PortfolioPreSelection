import investpy

# Imports
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
from pandas import ExcelWriter
import yfinance as yf
import pandas as pd
import datetime
import time

import sys
import os, fnmatch
import shutil

# imports
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np

import config
import datetime
from datetime import date, timedelta

def insert_df_column(df):
    columns = ["investing_symbol", "investing_country", "investing_company_name",
               "RSI(14)", "STOCH(9,6)", "STOCHRSI(14)", "MACD(12,26)", "ADX(14)",
               "W%R", "CCI(14)", "ATR(14)", "Highs/Lows(14)", "UltimateOscillator",
               "ROC", "Bull/BearPower(13)", "SMA_5", "SMA_10", "EMA_5", "EMA_10",
               "BUY", "BUY_SMA_EMA"]
    for column in columns:
        df.insert(len(df.columns), column, "-")
    return df

def get_investpy_data(ticker):
    country = ['united states']
    try:
        country = [config.DF_MATCH_YAHOO_INVESTING.loc[ticker, 'country']]
        ticker = config.DF_MATCH_YAHOO_INVESTING.loc[ticker, 'investing']
    except:
        if ticker.endswith('.DE'):
            country = ['germany']
            ticker = ticker[0:(len(ticker) - 3)]
        else:
            if ticker.endswith('.PA'):
                country = ['france']
                ticker = ticker[0:(len(ticker) - 3)]
            else:
                if ticker.endswith('.AS'):
                    country = ['netherlands']
                    ticker = ticker[0:(len(ticker) - 3)]

    return ticker, country

def get_ticker_match_investing(df_screener):
    len_df = len(df_screener)
    df_screener = df_screener.drop(df_screener[(df_screener.idx == '-')].index)
    df_screener.drop(df_screener[df_screener.symbol == 'CON.DE'].index, inplace=True)
    print("remove tickers with no index: ", len_df - len(df_screener))

    tickers = df_screener['symbol'].tolist()
    insert_df_column(df_screener)

    for ticker in tickers:
        symbol = ticker
        ticker, country = get_investpy_data(ticker)
        if symbol == 'ACT':
            print('ACT')

        try:
            if (symbol == 'AAP') or (symbol == 'AME') or (symbol == 'BA') or (symbol == 'CI') or (symbol == 'MA'):
                search_result_list = investpy.search_quotes(text=ticker, countries=country, products=['stocks'], n_results=3)
                search_result = search_result_list[1]
            else:
                search_result = investpy.search_quotes(text=ticker, countries=country, products=['stocks'], n_results=1)
            # information = search_result.retrieve_information()
            technical_indicators = search_result.retrieve_technical_indicators(interval='daily')

            df_screener['investing_symbol'] = np.where(df_screener['symbol'] == symbol,
                                                       search_result.symbol,
                                                       df_screener['investing_symbol'])
            df_screener['investing_country'] = np.where(df_screener['symbol'] == symbol,
                                                        search_result.country,
                                                        df_screener['investing_country'])
            df_screener['investing_company_name'] = np.where(df_screener['symbol'] == symbol,
                                                             search_result.name,
                                                             df_screener['investing_company_name'])
            df_screener['RSI(14)'] = np.where(df_screener['symbol'] == symbol,
                                              technical_indicators.signal[0],
                                              df_screener['RSI(14)'])
            df_screener['STOCH(9,6)'] = np.where(df_screener['symbol'] == symbol,
                                                 technical_indicators.signal[1],
                                                 df_screener['STOCH(9,6)'])
            df_screener['STOCHRSI(14)'] = np.where(df_screener['symbol'] == symbol,
                                                   technical_indicators.signal[2],
                                                   df_screener['STOCHRSI(14)'])
            df_screener['MACD(12,26)'] = np.where(df_screener['symbol'] == symbol,
                                                  technical_indicators.signal[3],
                                                  df_screener['MACD(12,26)'])
            df_screener['ADX(14)'] = np.where(df_screener['symbol'] == symbol,
                                              technical_indicators.signal[4],
                                              df_screener['ADX(14)'])
            df_screener['W%R'] = np.where(df_screener['symbol'] == symbol,
                                          technical_indicators.signal[5],
                                          df_screener['W%R'])
            df_screener['CCI(14)'] = np.where(df_screener['symbol'] == symbol,
                                              technical_indicators.signal[6],
                                              df_screener['CCI(14)'])
            df_screener['ATR(14)'] = np.where(df_screener['symbol'] == symbol,
                                              technical_indicators.signal[7],
                                              df_screener['ATR(14)'])
            df_screener['Highs/Lows(14)'] = np.where(df_screener['symbol'] == symbol,
                                                     technical_indicators.signal[8],
                                                     df_screener['Highs/Lows(14)'])
            df_screener['UltimateOscillator'] = np.where(df_screener['symbol'] == symbol,
                                                         technical_indicators.signal[9],
                                                         df_screener['UltimateOscillator'])
            df_screener['ROC'] = np.where(df_screener['symbol'] == symbol,
                                          technical_indicators.signal[10],
                                          df_screener['ROC'])
            df_screener['Bull/BearPower(13)'] = np.where(df_screener['symbol'] == symbol,
                                                         technical_indicators.signal[11],
                                                         df_screener['Bull/BearPower(13)'])
            buy = 0
            sell = 0
            neutral = 0
            for i in range(len(technical_indicators.signal)):
                if technical_indicators.signal[i] == 'buy':
                    buy = buy + 1
                elif technical_indicators.signal[i] == 'sell':
                    sell = sell + 1
                elif technical_indicators.signal[i] == 'neutral':
                    neutral = neutral + 1

            df_screener['BUY'] = np.where(df_screener['symbol'] == symbol,
                                          round(buy/(len(technical_indicators.signal) - 1)*100, 1),
                                          df_screener['BUY'])

            try:
                # sma_ema_indicators = investpy.moving_averages(name=ticker, country=country[0], product_type='stock',
                #                                              interval='daily')
                sma_ema_indicators = investpy.moving_averages(name=search_result.symbol, country=search_result.country, product_type='stock',
                                                              interval='daily')

                df_screener['EMA_5'] = np.where(df_screener['symbol'] == symbol,
                                                sma_ema_indicators.sma_signal[0],
                                                df_screener['EMA_5'])
                df_screener['EMA_10'] = np.where(df_screener['symbol'] == symbol,
                                                 sma_ema_indicators.sma_signal[1],
                                                 df_screener['EMA_10'])
                df_screener['SMA_5'] = np.where(df_screener['symbol'] == symbol,
                                                sma_ema_indicators.ema_signal[1],
                                                df_screener['SMA_5'])
                df_screener['SMA_10'] = np.where(df_screener['symbol'] == symbol,
                                                 sma_ema_indicators.ema_signal[1],
                                                 df_screener['SMA_10'])

                buy = 0
                sell = 0
                neutral = 0
                for i in range(len(sma_ema_indicators.sma_signal)):
                    if sma_ema_indicators.sma_signal[i] == 'buy':
                        buy = buy + 1
                    elif sma_ema_indicators.sma_signal[i] == 'sell':
                        sell = sell + 1
                    elif sma_ema_indicators.sma_signal[i] == 'neutral':
                        neutral = neutral + 1

                for i in range(len(sma_ema_indicators.ema_signal)):
                    if sma_ema_indicators.ema_signal[i] == 'buy':
                        buy = buy + 1
                    elif sma_ema_indicators.ema_signal[i] == 'sell':
                        sell = sell + 1
                    elif sma_ema_indicators.ema_signal[i] == 'neutral':
                        neutral = neutral + 1

                df_screener['BUY_SMA_EMA'] = np.where(df_screener['symbol'] == symbol,
                                                      round(buy/((len(sma_ema_indicators.ema_signal) + len(sma_ema_indicators.sma_signal)))*100, 1),
                                                      df_screener['BUY_SMA_EMA'])
            except:
                print("No sma ema Investing.com data for ",symbol)
        except:
            print("No Investing.com data for ",symbol)
        search_result = ""

    df_screener.to_csv(config.OUTPUT_DIR+'tmp.csv')

    return df_screener

