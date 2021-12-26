"""
#########################################################################################
# How to Predict Stock Volatility with Python
# https://python.plainenglish.io/how-to-predict-stock-volatility-with-python-46ae341ce804
#########################################################################################
"""

import yfinance as yf
from arch import arch_model
from arch.__future__ import reindexing
import math
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import datetime
import time
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

def get_volatility_perfo(df_screener):
    len_df = len(df_screener)
    df_screener = df_screener.drop(df_screener[(df_screener.idx == '-')].index)
    df_screener.drop(df_screener[df_screener.symbol == 'CON.DE'].index, inplace=True)
    print("remove tickers with no index: ",len_df - len(df_screener))

    tickers = df_screener['symbol'].tolist()
    df_screener.insert(len(df_screener.columns), "Daily_Volatility", "-")
    df_screener.insert(len(df_screener.columns), "Monthly_Volatility", "-")
    df_screener.insert(len(df_screener.columns), "Yearly_Volatility", "-")

    for ticker in tickers:

        if os.path.exists(config.DIR + ticker + '.csv'):
            df = pd.read_csv(config.DIR + ticker + '.csv')

            # Calculation of daily returns
            df['Return'] = 100 * (df['Close'].pct_change())

            # Calculation of daily, monthly, and annual volatility
            daily_volatility = df['Return'].std()
            # print('Daily volatility: ', '{:.2f}%'.format(daily_volatility))

            monthly_volatility = math.sqrt(21) * daily_volatility
            # print('Monthly volatility: ', '{:.2f}%'.format(monthly_volatility))

            annual_volatility = math.sqrt(252) * daily_volatility
            # print('Annual volatility: ', '{:.2f}%'.format(annual_volatility))

            df_screener['Daily_Volatility'] = np.where(df_screener['symbol'] == ticker, round(daily_volatility, 2), df_screener['Daily_Volatility'])
            df_screener['Monthly_Volatility'] = np.where(df_screener['symbol'] == ticker, round(monthly_volatility, 2), df_screener['Monthly_Volatility'])
            df_screener['Yearly_Volatility'] = np.where(df_screener['symbol'] == ticker, round(annual_volatility, 2), df_screener['Yearly_Volatility'])

    return df_screener









"""
# set date range for historical prices
end_time = datetime.date.today()
start_time = end_time - datetime.timedelta(days=4 * 365)

# reformat date range
end = end_time.strftime('%Y-%m-%d')
start = start_time.strftime('%Y-%m-%d')

ticker= "aapl"

stock_data = yf.download(ticker, start=start, end=end)

# Calculation of daily returns
stock_data['Return'] = 100 * (stock_data['Close'].pct_change())

stock_data.dropna(inplace=True)

fig = plt.figure()
fig.set_figwidth(12)
plt.plot(stock_data['Return'], label = 'Daily Returns')
plt.legend(loc='upper right')
plt.title('Daily Returns Over Time')
plt.show()

# Calculation of daily, monthly, and annual volatility
daily_volatility = stock_data['Return'].std()
print('Daily volatility: ', '{:.2f}%'.format(daily_volatility))

monthly_volatility = math.sqrt(21) * daily_volatility
print ('Monthly volatility: ', '{:.2f}%'.format(monthly_volatility))

annual_volatility = math.sqrt(252) * daily_volatility
print ('Annual volatility: ', '{:.2f}%'.format(annual_volatility ))





# Building GARCH Model
garch_model = arch_model(stock_data['Return'], p = 1, q = 1,
                      mean = 'constant', vol = 'GARCH', dist = 'normal')

gm_result = garch_model.fit(disp='off')
print(gm_result.params)

print('\n')

gm_forecast = gm_result.forecast(horizon = 5)
print(gm_forecast.variance[-1:])

rolling_predictions = []
test_size = 365

for i in range(test_size):
    train = stock_data['Return'][:-(test_size - i)]
    model = arch_model(train, p=1, q=1)
    model_fit = model.fit(disp='off')
    pred = model_fit.forecast(horizon=1)
    rolling_predictions.append(np.sqrt(pred.variance.values[-1, :][0]))

rolling_predictions = pd.Series(rolling_predictions, index=stock_data['Return'].index[-365:])


plt.figure(figsize=(10, 4))
plt.plot(rolling_predictions)
plt.title('Rolling Prediction')
plt.show()

plt.figure(figsize=(12,4))
plt.plot(stock_data['Return'][-365:])
plt.plot(rolling_predictions)
plt.title('Volatility Prediction - Rolling Forecast')
plt.legend(['True Daily Returns', 'Predicted Volatility'])
plt.show()
"""