# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import os, fnmatch
from datetime import date
import shutil
import pandas as pd
import numpy as np

sys.path.append("./load_yfinance_data/")
sys.path.append("./scraping/")
sys.path.append("./selection/")
sys.path.append("./init/")

#from stockstats import StockDataFrame as Sdf
import config
from load_yfinance_data import *

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def mk_directories(date_day):
    if not os.path.exists("./database"):
        os.makedirs("./database")

    if not os.path.exists("./screening_data"):
        os.makedirs("./screening_data")

    if not os.path.exists("./screening_data/" + date_day):
        os.makedirs("./screening_data/" + date_day)

    if not os.path.exists("./screening_data/" + date_day + "/stock_data/"):
        os.makedirs("./screening_data/" + date_day + "/stock_data/")
    config.STOCK_DATA_DIR = "./screening_data/" + date_day + "/stock_data/"

    if not os.path.exists("./screening_data/" + date_day + "/output/"):
        os.makedirs("./screening_data/" + date_day + "/output/")
    config.OUTPUT_DIR = "./screening_data/" + date_day + "/output/"

    if not os.path.exists("./screening_data/" + date_day + "/pool/"):
        os.makedirs("./screening_data/" + date_day + "/pool/")
    config.OUTPUT_POOL_DIR = "./screening_data/" + date_day + "/pool/"
    for f in os.listdir(config.OUTPUT_POOL_DIR):
        os.remove(os.path.join(config.OUTPUT_POOL_DIR, f))


if __name__ == '__main__':

    if (str(sys.argv[1]) == "--COLAB"):
        config.COLAB = True
    else:
        config.COLAB = False

    print(config.DATE)

    mk_directories(config.DATE)

    df_data_stock_list = get_data_finance(config.DATE)

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
