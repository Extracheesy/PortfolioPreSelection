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

from yscraping import get_YAHOO_ticker_list
from perfo_trend import get_trend_perfo
from perfo_return import get_return_perfo
from perfo_trend_ema import get_trend_bounce_ema
from perfo_volatility import get_volatility_perfo
from perfo_tech_ind import get_tech_indicator_perfo
from perfo_rating import get_rating_perfo
from perfo_yahoo_invest import get_ticker_match_investing
from perfo_signals import get_processed_signals

def lookup_fn(df, key_row, key_col):

    return df.iloc[key_row][key_col]


def remove_row(df,row):
    df.drop([row], axis=0, inplace=True)
    return df

# Create a data folder in your current dir.
def SaveData(df, filename):

    today = str(date.today())

    if (config.COLAB == True):
        df.to_csv("../drive/MyDrive/colab_results/MarketDailyColector/database/" + today + "/" + filename + "_" + today + ".csv")
    else:
        df.to_csv("./database/" + today + "/" + filename + "_" + today + ".csv")


def DownloadFromYahooData(df_ticker_list, date_time_str):
    if config.GET_DATA_FROM_CSV == True:
        df_ticker_list = pd.read_csv(config.OUTPUT_DIR + "dump_stock_info_valid_data.csv")
    else:
        date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
        
        # start_date = datetime.datetime.now() - datetime.timedelta(days=config.DATA_DURATION)
        # end_date = datetime.date.today()
        start_date = date_time_obj - datetime.timedelta(days=config.DATA_DURATION)
        end_date = date_time_obj
        
        for ticker in df_ticker_list["symbol"].unique():
            try:
                # Download historical data as CSV for each stock (makes the process faster)
                df = pdr.get_data_yahoo(ticker, start_date, end_date)
                df.to_csv(config.STOCK_DATA_DIR + f'{ticker}.csv')
            except:
                print("error get_data_yahoo: ",ticker)
                df_ticker_list.drop(df_ticker_list[df_ticker_list.symbol == ticker].index, inplace=True)

        print("dump info to dump_stock_info_valid_data.csv")

        df_ticker_list.to_csv(config.OUTPUT_DIR + "dump_stock_info_valid_data.csv")
        
        for index_name in config.INDEX:
            try:
                # Download historical data as CSV for each stock (makes the process faster)
                df = pdr.get_data_yahoo(index_name, start_date, end_date)
                df.to_csv(config.STOCK_DATA_DIR + f'{index_name}.csv')
            except:
                try:
                    tickerData = yf.Ticker(index_name)
                    df = tickerData.history(period='1d', start=start_date, end=end_date)
                    df.to_csv(config.STOCK_DATA_DIR + f'{index_name}.csv')
                except:
                    print("error Index from yahoo data: ",index_name)

    return df_ticker_list

def get_data_finance(date_time_str):

    df_ticker_list = pd.DataFrame()

    # Get ticker list
    df_ticker_list = get_YAHOO_ticker_list()

    # SaveData(df_ticker_list, "tickerdata")

    df_ticker_list = DownloadFromYahooData(df_ticker_list, date_time_str)

    if 'index' in df_ticker_list.columns:
        df_ticker_list = df_ticker_list.drop(['index'], axis=1)
    if "Unnamed: 0" in df_ticker_list.columns:
        df_ticker_list = df_ticker_list.drop("Unnamed: 0", axis=1)

    df_ticker_list = get_processed_signals(df_ticker_list)

    df_ticker_list = get_ticker_match_investing(df_ticker_list)
    # df_ticker_list = get_tech_indicator_perfo(df_ticker_list) # Replaced

    # df_ticker_list = get_rating_perfo(df_ticker_list) # to be completed

    df_ticker_list = get_trend_perfo(df_ticker_list)

    df_ticker_list = get_return_perfo(df_ticker_list)

    df_ticker_list = get_volatility_perfo(df_ticker_list)

    #df_ticker_list = get_trend_bounce_ema(df_ticker_list)

    df_ticker_list.to_csv(config.OUTPUT_DIR + "Final_Screener_list.csv")

    return df_ticker_list




