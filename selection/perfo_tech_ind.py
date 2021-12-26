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


def get_investpy_data(ticker):

    country = ['united states']

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


def get_tech_indicator_perfo(df_screener):
    len_df = len(df_screener)
    df_screener = df_screener.drop(df_screener[(df_screener.idx == '-')].index)
    df_screener.drop(df_screener[df_screener.symbol == 'CON.DE'].index, inplace=True)
    print("remove tickers with no index: ",len_df - len(df_screener))

    tickers = df_screener['symbol'].tolist()
    df_screener.insert(len(df_screener.columns), "RSI(14)", "-")
    df_screener.insert(len(df_screener.columns), "STOCH(9,6)", "-")
    df_screener.insert(len(df_screener.columns), "STOCHRSI(14)", "-")
    df_screener.insert(len(df_screener.columns), "MACD(12,26)", "-")
    df_screener.insert(len(df_screener.columns), "ADX(14)", "-")
    df_screener.insert(len(df_screener.columns), "W%R", "-")
    df_screener.insert(len(df_screener.columns), "CCI(14)", "-")
    df_screener.insert(len(df_screener.columns), "ATR(14)", "-")
    df_screener.insert(len(df_screener.columns), "Highs/Lows(14)", "-")
    df_screener.insert(len(df_screener.columns), "UltimateOscillator", "-")
    df_screener.insert(len(df_screener.columns), "ROC", "-")
    df_screener.insert(len(df_screener.columns), "Bull/BearPower(13)", "-")
    df_screener.insert(len(df_screener.columns), "SMA_5", "-")
    df_screener.insert(len(df_screener.columns), "SMA_10", "-")
    df_screener.insert(len(df_screener.columns), "EMA_5", "-")
    df_screener.insert(len(df_screener.columns), "EMA_10", "-")
    df_screener.insert(len(df_screener.columns), "BUY", "-")
    df_screener.insert(len(df_screener.columns), "BUY_SMA_EMA", "-")

    """
    df_screener.insert(len(df_screener.columns), "SELL", "-")
    df_screener.insert(len(df_screener.columns), "NEUTRAL", "-")
    """

    for ticker in tickers:
        if os.path.exists(config.STOCK_DATA_DIR + ticker + '.csv'):
            start_date = datetime.datetime.now() - datetime.timedelta(days=config.DATA_DURATION)
            end_date = datetime.date.today()

            """
            df = investpy.get_stock_historical_data(stock="AAPL",
                                                    country='United States',
                                                    from_date=start_date.strftime("%m/%d/%Y"),
                                                    to_date=end_date.strftime("%m/%d/%Y"))
            """
            #try:
            ticker_tmp = ticker

            print(ticker)

            ticker, country = get_investpy_data(ticker)

            if ticker == 'ACA':
                print('ACA')

            search_result = investpy.search_quotes(text=ticker, countries=country, products=['stocks'], n_results=1)
            information = search_result.retrieve_information()
            # print(information)

            technical_indicators = search_result.retrieve_technical_indicators(interval='daily')

            if ticker == 'ACA':
                print('ACA')
                toto = investpy.indices.get_index_countries()
                titi = investpy.indices.get_indices_list(country=None)
                ticker = 'ACAp'
                sma_ema_indicators = investpy.moving_averages(name=ticker, country='france', product_type='stock',
                                                              interval='daily')
            sma_ema_indicators = investpy.moving_averages(name=ticker, country=country[0], product_type='stock',
                                                          interval='daily')

            # print(technical_indicators)
            ticker = ticker_tmp
            df_screener['RSI(14)'] = np.where(df_screener['symbol'] == ticker,
                                              technical_indicators.signal[0],
                                              df_screener['RSI(14)'])
            df_screener['STOCH(9,6)'] = np.where(df_screener['symbol'] == ticker,
                                                 technical_indicators.signal[1],
                                                 df_screener['STOCH(9,6)'])
            df_screener['STOCHRSI(14)'] = np.where(df_screener['symbol'] == ticker,
                                                   technical_indicators.signal[2],
                                                   df_screener['STOCHRSI(14)'])
            df_screener['MACD(12,26)'] = np.where(df_screener['symbol'] == ticker,
                                                  technical_indicators.signal[3],
                                                  df_screener['MACD(12,26)'])
            df_screener['ADX(14)'] = np.where(df_screener['symbol'] == ticker,
                                              technical_indicators.signal[4],
                                              df_screener['ADX(14)'])
            df_screener['W%R'] = np.where(df_screener['symbol'] == ticker,
                                          technical_indicators.signal[5],
                                          df_screener['W%R'])
            df_screener['CCI(14)'] = np.where(df_screener['symbol'] == ticker,
                                              technical_indicators.signal[6],
                                              df_screener['CCI(14)'])
            df_screener['ATR(14)'] = np.where(df_screener['symbol'] == ticker,
                                              technical_indicators.signal[7],
                                              df_screener['ATR(14)'])
            df_screener['Highs/Lows(14)'] = np.where(df_screener['symbol'] == ticker,
                                                     technical_indicators.signal[8],
                                                     df_screener['Highs/Lows(14)'])
            df_screener['UltimateOscillator'] = np.where(df_screener['symbol'] == ticker,
                                                         technical_indicators.signal[9],
                                                         df_screener['UltimateOscillator'])
            df_screener['ROC'] = np.where(df_screener['symbol'] == ticker,
                                          technical_indicators.signal[10],
                                          df_screener['ROC'])
            df_screener['Bull/BearPower(13)'] = np.where(df_screener['symbol'] == ticker,
                                                         technical_indicators.signal[11],
                                                         df_screener['Bull/BearPower(13)'])
            df_screener['EMA_5'] = np.where(df_screener['symbol'] == ticker,
                                            sma_ema_indicators.sma_signal[0],
                                            df_screener['EMA_5'])
            df_screener['EMA_10'] = np.where(df_screener['symbol'] == ticker,
                                             sma_ema_indicators.sma_signal[1],
                                             df_screener['EMA_10'])
            df_screener['SMA_5'] = np.where(df_screener['symbol'] == ticker,
                                            sma_ema_indicators.ema_signal[1],
                                            df_screener['SMA_5'])
            df_screener['SMA_10'] = np.where(df_screener['symbol'] == ticker,
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
            df_screener['BUY_SMA_EMA'] = np.where(df_screener['symbol'] == ticker,
                                                  round(buy/(len(sma_ema_indicators.ema_signal) + len(sma_ema_indicators.sma_signal) - 1)*100, 1),
                                                  df_screener['BUY_SMA_EMA'])
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

            df_screener['BUY'] = np.where(df_screener['symbol'] == ticker,
                                          round(buy/(len(technical_indicators.signal) - 1)*100, 1),
                                          df_screener['BUY'])


            """
            df_screener['SELL'] = np.where(df_screener['symbol'] == ticker,
                                                     round(sell/(len(technical_indicators.signal) - 1)*100, 1),
                                                     df_screener['SELL'])
            
            df_screener['NEUTRAL'] = np.where(df_screener['symbol'] == ticker,
                                                     round(neutral/(len(technical_indicators.signal) - 1)*100, 1),
                                                     df_screener['NEUTRAL'])
            """
            #except:
            #    print("Investpy no data for ",ticker)

    return df_screener