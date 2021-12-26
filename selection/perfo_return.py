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


def cp_df_columns_to_df(df_screener, df):

    df = df.set_index(df.Ticker)
    df = df.drop(columns=['Ticker', 'Index'])

    df_screener = df_screener.set_index(df_screener.symbol)

    combined_df = pd.concat([df_screener, df], axis=1)
    combined_df = combined_df.reset_index(drop=True)
    return combined_df

def get_return_perfo(df_screener):
    len_df = len(df_screener)
    df_screener = df_screener.drop(df_screener[(df_screener.idx == '-')].index)
    df_screener.drop(df_screener[df_screener.symbol == 'CON.DE'].index, inplace=True)
    print("remove tickers with no index: ",len_df - len(df_screener))

    exportList = pd.DataFrame(
        columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

    list_df_export = []
    df_result = pd.DataFrame()
    for index_name in config.INDEX:
        tickers = df_screener[df_screener['idx'] == index_name]['symbol'].tolist()

        returns_multiples_year = []
        returns_tickers_year = []

        returns_multiples_half_year = []
        returns_tickers_half_year = []

        returns_multiples_last_month = []
        returns_tickers_last_month = []

        returns_multiples_last_week = []
        returns_tickers_last_week = []

        # Index Returns
        index_df = pd.read_csv(config.STOCK_DATA_DIR+index_name+'.csv')
        index_df_year = index_df.tail(int(config.YEAR_OF_TRADE))
        index_df_year.reset_index(inplace=True, drop=True)
        index_df_half_year = index_df.tail(int(config.YEAR_OF_TRADE/2))
        index_df_half_year.reset_index(inplace=True, drop=True)
        index_df_last_month = index_df.tail(int(config.YEAR_OF_TRADE/12))
        index_df_last_month.reset_index(inplace=True, drop=True)
        index_df_last_week = index_df.tail(int(config.YEAR_OF_TRADE/12/4))
        index_df_last_week.reset_index(inplace=True, drop=True)

        index_df_year['Percent Change'] = index_df_year['Adj Close'].pct_change()
        lst_index_return_year = (index_df_year['Percent Change'] + 1).cumprod()
        index_return_year = lst_index_return_year[len(lst_index_return_year) - 1]

        index_df_half_year['Percent Change'] = index_df_half_year['Adj Close'].pct_change()
        lst_index_return_half_year = (index_df_half_year['Percent Change'] + 1).cumprod()
        index_return_half_year = lst_index_return_half_year[len(lst_index_return_half_year) - 1]

        index_df_last_month['Percent Change'] = index_df_last_month['Adj Close'].pct_change()
        lst_index_return_last_month = (index_df_last_month['Percent Change'] + 1).cumprod()
        index_return_last_month = lst_index_return_last_month[len(lst_index_return_last_month) - 1]

        index_df_last_week['Percent Change'] = index_df_last_week['Adj Close'].pct_change()
        lst_index_return_last_week = (index_df_last_week['Percent Change'] + 1).cumprod()
        index_return_last_week = lst_index_return_last_week[len(lst_index_return_last_week) - 1]

        for ticker in tickers:
            #if ticker == 'VOW3.DE':
            #    print("DEBUG")
            #    df = pdr.get_data_yahoo(ticker, start_date, end_date)
            #    df.to_csv(config.DIR + f'{ticker}.csv')
            if os.path.exists(config.STOCK_DATA_DIR+ticker+'.csv'):
                df = pd.read_csv(config.STOCK_DATA_DIR+ticker+'.csv')
                df_year = df.tail(int(config.YEAR_OF_TRADE))
                df_year.reset_index(inplace=True, drop=True)
                df_half_year = df.tail(int(config.YEAR_OF_TRADE / 2))
                df_half_year.reset_index(inplace=True, drop=True)
                df_last_month = df.tail(int(config.YEAR_OF_TRADE / 12))
                df_last_month.reset_index(inplace=True, drop=True)
                df_last_week = df.tail(int(config.YEAR_OF_TRADE / 12 / 4))
                df_last_week.reset_index(inplace=True, drop=True)

                # Calculating returns relative to the market (returns multiple)
                df_year['Percent Change'] = df_year['Adj Close'].pct_change()
                lst_stock_return_year = (df_year['Percent Change'] + 1).cumprod()
                stock_return_year = lst_stock_return_year[len(lst_stock_return_year)-1]
                returns_tickers_year.extend([round(stock_return_year,2)])

                returns_multiple_year = round((stock_return_year / index_return_year), 2)
                returns_multiples_year.extend([returns_multiple_year])

                df_half_year['Percent Change'] = df_half_year['Adj Close'].pct_change()
                lst_stock_return_half_year = (df_half_year['Percent Change'] + 1).cumprod()
                stock_return_half_year = lst_stock_return_half_year[len(lst_stock_return_half_year)-1]
                returns_tickers_half_year.extend([round(stock_return_half_year,2)])

                returns_multiple_half_year = round((stock_return_half_year / index_return_half_year), 2)
                returns_multiples_half_year.extend([returns_multiple_half_year])

                df_last_month['Percent Change'] = df_last_month['Adj Close'].pct_change()
                lst_stock_return_last_month = (df_last_month['Percent Change'] + 1).cumprod()
                stock_return_last_month = lst_stock_return_last_month[len(lst_stock_return_last_month)-1]
                returns_tickers_last_month.extend([round(stock_return_last_month,2)])

                returns_multiple_last_month = round((stock_return_last_month / index_return_last_month), 2)
                returns_multiples_last_month.extend([returns_multiple_last_month])

                df_last_week['Percent Change'] = df_last_week['Adj Close'].pct_change()
                lst_stock_return_last_week = (df_last_week['Percent Change'] + 1).cumprod()
                stock_return_last_week = lst_stock_return_last_week[len(lst_stock_return_last_week)-1]
                returns_tickers_last_week.extend([round(stock_return_last_week,2)])

                returns_multiple_last_week = round((stock_return_last_week / index_return_last_week), 2)
                returns_multiples_last_week.extend([returns_multiple_last_week])

                # time.sleep(1)
            else:
                print(f"Could not find data file on {ticker}")

        rs_df = pd.DataFrame(list(zip(tickers,
                                      returns_tickers_year, returns_multiples_year,
                                      returns_tickers_half_year, returns_multiples_half_year,
                                      returns_tickers_last_month, returns_multiples_last_month,
                                      returns_tickers_last_week, returns_multiples_last_week)),
                             columns=['Ticker',
                                      'Return_year','Returns_multiple_year',
                                      'Return_half_year','Returns_multiple_half_year',
                                      'Return_last_month','Returns_multiple_last_month',
                                      'Return_last_week','Returns_multiple_last_week'])
        rs_df['RS_Rating_week'] = round(rs_df.Returns_multiple_last_week.rank(pct=True) * 100, 2)
        rs_df['RS_Rating_month'] = round(rs_df.Returns_multiple_last_month.rank(pct=True) * 100, 2)
        rs_df['RS_Rating_half_year'] = round(rs_df.Returns_multiple_half_year.rank(pct=True) * 100, 2)
        rs_df['RS_Rating_year'] = round(rs_df.Returns_multiple_year.rank(pct=True) * 100, 2)

        #rs_df.insert(len(rs_df.columns), "idx",index_name)
        rs_df.insert(1, "Index", index_name)

        # if config.KEEP_BEST == True:
            # Creating dataframe of only top 30%
        #    rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(config.BEST_PERCENT)]
        df_export = rs_df.copy()
        #list_df_export.extend(df_export)

        df_result = pd.concat([df_result , df_export])

    df_result = df_result.sort_values(by='Returns_multiple_last_week', ascending=False)

    #df_result = pd.concat(list_df_export)
    df_result.to_csv(config.OUTPUT_DIR+"ScreenReturn.csv")

    df_screener = cp_df_columns_to_df(df_screener, df_result)

    return df_screener







