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

#from stockstats import StockDataFrame as Sdf
from load_yfinance_data import *


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def mk_directories():
    COLAB = True

    if not os.path.exists("./database"):
        os.makedirs("./database")

    today = date.today()

    if not os.path.exists("./database/" + str(today)):
        os.makedirs("./database/" + str(today))

    if (COLAB == True):
        os.makedirs("../drive/MyDrive/colab_results/MarketDailyColector/database/" + str(today))


if __name__ == '__main__':

    mk_directories()

    df_data_stock_list = get_data_finance()

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
