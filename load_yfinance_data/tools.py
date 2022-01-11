import os, fnmatch
import pandas as pd
import config
import datetime
from datetime import date, timedelta

def merge_csv_to_df(path, pattern):
    current_dir = os.getcwd()
    os.chdir(path)

    listOfFilesToRemove = os.listdir('./')
    #pattern = "*.csv"
    li = []
    for entry in listOfFilesToRemove:
        if fnmatch.fnmatch(entry, pattern):
            print("csv file : ",entry)
            df = pd.read_csv(entry, index_col=None, header=0)
            li.append(df)

    df_frame = pd.concat(li, axis=0, ignore_index=True)

    # today = date.today()
    # df_frame.to_csv("stocks_movments_merged_" + str(today) + ".csv", index=True, sep='\t')

    os.chdir(current_dir)

    return df_frame

def split_list(a_list, size_split):
    return a_list[:size_split], a_list[size_split:]

def split_list_into_list(list):
    # split a list into a list of breakdown list
    len_list = len(list)
    len_split_list = int(len_list / config.NB_SPLIT_LIST_SYMBOL)

    rest_of_the_list = list
    global_split_list = []

    for i in range(config.NB_SPLIT_LIST_SYMBOL):
        splited_list, rest_of_the_list = split_list(rest_of_the_list, len_split_list)
        global_split_list.append(splited_list)

    if len(rest_of_the_list) > 1:
        global_split_list.append(rest_of_the_list)

    return global_split_list