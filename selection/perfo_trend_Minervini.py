"""
https://towardsdatascience.com/making-a-stock-screener-with-python-4f591b198261

Python program based on Mark Minervini’s Trend Template (the 8 principles on selecting the best stocks)
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

from yahoo_fin import stock_info as si
import yfinance as yf

import config
import datetime
from datetime import date, timedelta

def get_trend_perfo(df_screener):

    #start_date = datetime.datetime.now() - datetime.timedelta(days=config.DATA_DURATION)
    #end_date = datetime.date.today()

    df_screener.insert(len(df_screener.columns), "Minervini", "-")
    df_screener.insert(len(df_screener.columns), "RS_Rating", "-")

    exportList = pd.DataFrame(
        columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

    index_list = np.unique(df_screener['exchange']).tolist()

    #for index_name in config.INDEX:
    for index_name in index_list:

        
        yf_stock = yf.Ticker(index_name)

        tickers = df_screener[df_screener['exchange'] == index_name]['symbol'].tolist()
        returns_multiples = []
        returns_tickers = []



        # Index Returns
        index_df = pd.read_csv(config.STOCK_DATA_DIR+index_name+'.csv')
        index_df['Percent Change'] = index_df['Adj Close'].pct_change()
        lst_index_return = (index_df['Percent Change'] + 1).cumprod()
        index_return = lst_index_return[len(lst_index_return) - 1]

        # Find top 30% performing stocks (relative to the S&P 500)
        for ticker in tickers:
            #if ticker == 'VOW3.DE':
            #    print("DEBUG")
            #    df = pdr.get_data_yahoo(ticker, start_date, end_date)
            #    df.to_csv(config.DIR + f'{ticker}.csv')
            if (os.path.exists(config.STOCK_DATA_DIR+ticker+'.csv')) and (ticker != 'CON.DE'):
                df = pd.read_csv(config.STOCK_DATA_DIR+ticker+'.csv')
                # Calculating returns relative to the market (returns multiple)
                df['Percent Change'] = df['Adj Close'].pct_change()
                lst_stock_return = (df['Percent Change'] + 1).cumprod()
                stock_return = lst_stock_return[len(lst_stock_return)-1]
                returns_tickers.extend([stock_return])

                returns_multiple = round((stock_return / index_return), 2)
                returns_multiples.extend([returns_multiple])

                # print(f'Ticker: {ticker}; Returns Multiple against {index_name}: {returns_multiple}\n')
                # time.sleep(1)
            else:
                print(f"Could not find data file on {ticker}")

        rs_df = pd.DataFrame(list(zip(tickers, returns_tickers, returns_multiples)), columns=['Ticker', 'Return_ticker','Returns_multiple'])
        rs_df['RS_Rating'] = rs_df.Returns_multiple.rank(pct=True) * 100
        if config.KEEP_BEST == True:
            # Creating dataframe of only top 30%
            rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(config.BEST_PERCENT)]

        # Checking Minervini conditions of top 30% of stocks in given list
        rs_stocks = rs_df['Ticker']
        for stock in rs_stocks:
            try:
                df = pd.read_csv(config.STOCK_DATA_DIR + stock + '.csv', index_col=0)
                sma = [50, 150, 200]
                for x in sma:
                    df["SMA_" + str(x)] = round(df['Adj Close'].rolling(window=x).mean(), 2)

                # Storing required values
                currentClose = df["Adj Close"][-1]
                moving_average_50 = df["SMA_50"][-1]
                moving_average_150 = df["SMA_150"][-1]
                moving_average_200 = df["SMA_200"][-1]
                low_of_52week = round(min(df["Low"][-260:]), 2)
                high_of_52week = round(max(df["High"][-260:]), 2)
                RS_Rating = round(rs_df[rs_df['Ticker'] == stock].RS_Rating.tolist()[0])

                try:
                    moving_average_200_20 = df["SMA_200"][-20]
                except Exception:
                    moving_average_200_20 = 0

                # Condition 1: Current Price > 150 SMA and > 200 SMA
                condition_1 = currentClose > moving_average_150 > moving_average_200

                # Condition 2: 150 SMA and > 200 SMA
                condition_2 = moving_average_150 > moving_average_200

                # Condition 3: 200 SMA trending up for at least 1 month
                condition_3 = moving_average_200 > moving_average_200_20

                # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
                condition_4 = moving_average_50 > moving_average_150 > moving_average_200

                # Condition 5: Current Price > 50 SMA
                condition_5 = currentClose > moving_average_50

                # Condition 6: Current Price is at least 30% above 52 week low
                condition_6 = currentClose >= (1.3 * low_of_52week)

                # Condition 7: Current Price is within 25% of 52 week high
                condition_7 = currentClose >= (.75 * high_of_52week)

                # If all conditions above are true, add stock to exportList
                if (condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7):
                    yf_stock = yf.Ticker(stock)
                    sector = yf_stock.info['sector']

                    exportList = exportList.append({'Stock': stock, 'Index': index_name,'Sector': sector,"RS_Rating": RS_Rating, "50 Day MA": moving_average_50,
                                                    "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200,
                                                    "52 Week Low": low_of_52week, "52 week High": high_of_52week},
                                                   ignore_index=True)
                    print(stock + " made the Minervini requirements")
                    df_screener['Minervini'] = np.where(df_screener['symbol'] == stock, 'UP', df_screener['Minervini'])
                    df_screener['RS_Rating'] = np.where(df_screener['symbol'] == stock, RS_Rating, df_screener['RS_Rating'])
            except Exception as e:
                print(e)
                print(f"Could not gather data on {stock}")

    exportList = exportList.sort_values(by='RS_Rating', ascending=False)
    exportList.to_csv(config.OUTPUT_DIR + "ScreenTrendOutput.csv")

    return df_screener





