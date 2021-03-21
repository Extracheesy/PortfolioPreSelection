import sys
import os, fnmatch
import shutil

# imports
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np

# from google.colab import files

import datetime
from datetime import date, timedelta

from yscraping import get_YAHOO_ticker_list

def lookup_fn(df, key_row, key_col):

    return df.iloc[key_row][key_col]


def remove_row(df,row):
    df.drop([row], axis=0, inplace=True)
    return df

# Create a data folder in your current dir.
def SaveData(df, filename):
    COLAB = False

    today = str(date.today())

    if COLAB == True:
        df.to_csv("../drive/MyDrive/colab_results/MarketDailyColector/database/" + today + "/" + filename + "_" + today + ".csv")
    else:
        df.to_csv("./database/" + today + "/" + filename + "_" + today + ".csv")


def DownloadFromYahooDailyData(df_ticker_list):

    for value in df_ticker_list["Symbol"].unique():
        #nb_years = 5 * 52  # 5 * 12 months for 5 years
        #today = date.today()
        #start_date = today - timedelta(weeks=nb_years)
        #data = pdr.get_data_yahoo(ticker, start=start_date, end=today)

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = '5m'
        df_data = yf.download(value, period="60d", interval=interval)

        if len(df_data) == 0:
            interval = '15m'
            df_data = yf.download(value, period="60d", interval=interval)
            if len(df_data) == 0:
                interval = '30m'
                df_data = yf.download(value, period="60d", interval=interval)
                if len(df_data) == 0:
                    interval = "non_data"

        SaveData(df_data, "daily_data_" + interval + "_" + value)


def get_data_finance():

    df_ticker_list = get_YAHOO_ticker_list()

    SaveData(df_ticker_list, "tickerlist")

    DownloadFromYahooDailyData(df_ticker_list)

    return df_ticker_list




