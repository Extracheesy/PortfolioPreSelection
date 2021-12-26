"""
# https://levelup.gitconnected.com/automate-your-stock-screening-using-python-9107dda724c3
"""

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

def add_EMA(price, day):
  return price.ewm(span=day).mean()

def add_STOCH(close, low, high, period, k, d=0):
    STOCH_K = ((close - low.rolling(window=period).min()) / (high.rolling(window=period).max() - low.rolling(window=period).min())) * 100
    STOCH_K = STOCH_K.rolling(window=k).mean()
    if d == 0:
      return STOCH_K
    else:
      STOCH_D = STOCH_K.rolling(window=d).mean()
      return STOCH_D

def check_bounce_EMA(df):
  candle1 = df.iloc[-1]
  candle2 = df.iloc[-2]
  cond1 = candle1['EMA18'] > candle1['EMA50'] > candle1['EMA100']
  cond2 = candle1['STOCH_%K(5,3,3)'] <= 30 or candle1['STOCH_%D(5,3,3)'] <= 30
  cond3 = candle2['Low'] < candle2['EMA50'] and candle2['Close'] > candle2['EMA50'] and candle1['Low'] > candle1 ['EMA50']

  return cond1 and cond2 and cond3

def get_trend_bounce_ema(df_screener):

    #start_date = datetime.datetime.now() - datetime.timedelta(days=config.DATA_DURATION)
    #end_date = datetime.date.today()
    df_screener.drop(df_screener[df_screener.symbol == 'CON.DE'].index, inplace=True)
    df_screener.insert(len(df_screener.columns), "EMA_Bounce", "-")

    screened_list = []
    for index_name in config.INDEX:
        tickers = df_screener[df_screener['idx'] == index_name]['symbol'].tolist()

        for ticker in tickers:
            #print(ticker)
            if os.path.exists(config.DIR+ticker+'.csv'):
                df = pd.read_csv(config.DIR+ticker+'.csv')

                close = df['Close']
                low = df['Low']
                open = df['Open']
                high = df['High']
                df['EMA18'] = add_EMA(close, 18)
                df['EMA50'] = add_EMA(close, 50)
                df['EMA100'] = add_EMA(close, 100)
                df['STOCH_%K(5,3,3)'] = add_STOCH(close, low, high, 5, 3)
                df['STOCH_%D(5,3,3)'] = add_STOCH(close, low, high, 5, 3, 3)

                # if all 3 conditions are met, add stock into screened list
                if check_bounce_EMA(df):
                    df_screener['EMA_Bounce'] = np.where(df_screener['symbol'] == ticker, 'UP', df_screener['EMA_Bounce'])

    return df_screener
