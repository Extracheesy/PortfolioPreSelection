"""
# https://codingandfun.com/evaluate-companies-liquidity-with-python/
Liquidity ratios focus on short term liabilities:
- Working Capital = Current Assets – Current Liabilities
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Cash + Marketable Securities + Receivables) / Current Liabilities
- Cash Ratio = Cash + Marketable Securities/ Current Liabilities
"""

# Imports
from pandas_datareader import data as pdr
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

# def get_return_volatility(df_screener):
