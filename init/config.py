import pandas as pd
import numpy as np
from datetime import date

COLAB = True
WIKI = True
NASDAQ_SCRAPING = False
NASDAQ_100 = True
NO_SCRAPING = True
GET_NYSE = False

KEEP_BEST = True
#BEST_PERCENT = 0.70 # keep best 30%
BEST_PERCENT = 0.10 # keep best 90%

DATA_DURATION = 365
YEAR_OF_TRADE = 250

DATE = str(date.today())
#DATE = "2021-12-30"

READ_LIST_FROM_PREVIOUS_CSV = False # Data downloaded from Yfinance
GET_DATA_FROM_CSV = False # Data downloaded from Yfinance
# READ_LIST_FROM_PREVIOUS_CSV = True # Data reading from previous download
# GET_DATA_FROM_CSV = True # Data reading from previous download

DRIVER_PATH = "./chromedriver.exe"

DIR = "./screening_data/"
STOCK_DATA_DIR = ""
OUTPUT_DIR = ""

"""
region_idx= 
{ 'US & Canada' : ['^GSPC', '^DJI', '^IXIC', '^RUT','^GSPTSE'],
  'Latin America' : ['^BVSP', '^MXX', '^IPSA'],
  'East Asia' : ['^N225', '^HSI', '000001.SS', '399001.SZ', '^TWII', '^KS11'],
  'ASEAN & Oceania' : ['^STI', '^JKSE', '^KLSE','^AXJO',  '^NZ50'],
  'South & West Asia' : ['^BSESN', '^TA125.TA'],
  'Europe' : ['^FTSE', '^GDAXI', '^FCHI', '^STOXX50E','^N100', '^BFX']
}
"""


YAHOO = ['MUV2.DE', 'FRE.DE', 'VNA.DE', 'SU.PA', 'ML.PA', 'MC.PA', 'HO.PA', 'EN.PA', 'EL.PA', 'DG.PA', 'CS.PA', 'CAP.PA', 'BNP.PA', 'BN.PA', 'ALO.PA', 'ACA.PA']
COUNTRY = ['germany', 'germany', 'germany', 'france','france', 'france', 'france', 'france', 'france', 'france', 'france', 'france', 'france', 'france', 'france', 'france']
INVESTING = ['MUVGn', 'FREG', 'VNAn', 'SCHN', 'MICP', 'LVMH', 'TCFP', 'BOUY', 'ESLX', 'SGEF', 'AXAF', 'CAPP', 'BNPP', 'DANO', 'ALSO', 'CAGR']

# initialize data of lists.
data = {'country': COUNTRY,
        'investing': INVESTING}

# Creates pandas DataFrame.
DF_MATCH_YAHOO_INVESTING = pd.DataFrame(data, index=YAHOO)

INDEX = ['^NYA','^FCHI','^GDAXI','^DJI','^IXIC','^GSPC']
INDEX_FULL_NAME = ['NYSE', 'CAC40', 'XETR','DJI', 'NASDAQ', 'SPX']

AMERICAN_INDEX = ['NYSE', 'NASDAQ', 'SPX']

# initialize data of lists.
data_tradingview = {'index_tradingview': INDEX_FULL_NAME}

# Creates pandas DataFrame.
DF_MATCH_INDEX_FULLNAME = pd.DataFrame(data_tradingview, index=INDEX)
