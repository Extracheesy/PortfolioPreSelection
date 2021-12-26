# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import mpl_finance

import fix_yahoo_finance as yf
from yahoo_fin.stock_info import *

# Import the os module
import os
import config

# Function for bb strategy
def implement_bb_signal_approach(data, lower_bb, upper_bb):
    bb_signal = []
    for i in range(len(data)):
        # Two consecutive rows comparison for trend detection
        # Scenario 1 Both Below Lower Band - Buy
        if data[i - 1] < lower_bb[i - 1] and data[i] < lower_bb[i]:
            signal = 1
            bb_signal.append(signal)
        # Scenario 2 Middle to Upper - Sell
        elif data[i - 1] < upper_bb[i - 1] and data[i] > upper_bb[i]:
            signal = -1
            bb_signal.append(signal)
        # Scenario 3 Both Upper - Sell
        elif data[i - 1] > upper_bb[i - 1] and data[i] > upper_bb[i]:
            signal = -1
            bb_signal.append(signal)
        # Scenario 4 Middle to Lower - Buy
        elif data[i - 1] > lower_bb[i - 1] and data[i] < lower_bb[i]:
            signal = 1
            bb_signal.append(signal)
        else:
            bb_signal.append(0)

    return bb_signal


def get_sma(data, window):
    sma = data.rolling(window=window).mean()
    return sma

# Bands Calculation
def get_bb(data, sma, window):
    std = data.rolling(window=window).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    return upper_bb, lower_bb


def implement_rsi_signal_approach(close, window):
    # Price increase or decrease over previous day
    dif = close.diff()
    dif = dif[1:]

    # pos_m identifies stock price going up
    # neg_m udentifies stock price going down
    pos_m, neg_m = dif.copy(), dif.copy()
    pos_m[pos_m < 0] = 0
    neg_m[neg_m > 0] = 0

    # Positive Rolling Mean Exponential
    prme = pos_m.ewm(span=window).mean()
    # Negative Rolling Mean Exponential
    nrme = neg_m.abs().ewm(span=window).mean()

    # Ratio of magnitude of up move to down move
    RSE = prme / nrme
    RSIE = 100.0 - (100.0 / (1.0 + RSE))

    return RSIE

def get_processed_signals(df_screener):
    df_screener.insert(len(df_screener.columns), "Signal_RSI", "-")
    df_screener.insert(len(df_screener.columns), "Signal_Bollinger", "-")

    tickers = df_screener['symbol'].tolist()

    approaches = ['BB','RSI']
    methods = ['BPS','BHPS','BPHS']

    for ticker in tickers:
        if (os.path.exists(config.STOCK_DATA_DIR + ticker + '.csv')) and (ticker != 'CON.DE'):
            df = pd.read_csv(config.STOCK_DATA_DIR + ticker + '.csv')

            df.Open = df.Open.round(2)
            df.High = df.High.round(2)
            df.Low = df.Low.round(2)
            df.Close = df.Close.round(2)
            df['Adj Close'] = df['Adj Close'].round(2)

            df = df[['Date','Open','High','Low','Close']]
            df = df.rename({'Date':'date','High':'high','Low':'low','Open':'open','Close':'close'},axis=1)
            df = df.set_index('date')
            df.index = pd.to_datetime(df.index)

            # Moving Averages Calculation
            df['sma_20'] = get_sma(df['close'], 20)
            # Bollinger Bands calculation
            df['upper_bb'], df['lower_bb'] = get_bb(df['close'], df['sma_20'], 20)

            # Signal Generation wrt bands
            for approach in approaches:
                # BB
                if approach == "BB":
                    bb_signal = implement_bb_signal_approach(df['close'], df['lower_bb'], df['upper_bb'])
                    bb_signal = pd.DataFrame(bb_signal).rename(columns = {0:'bb_signal'}).set_index(df.index)
                    df = df.join(bb_signal, how = 'inner')
                    df.reset_index(inplace=True)
                    #df.to_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/df_bb_out.csv")
                    #print(df.bb_signal.value_counts(dropna=False))
                # RSI
                else:
                    rsi_signal = implement_rsi_signal_approach(df['close'], 14)
                    rsi_signal = pd.DataFrame(rsi_signal).rename(columns={'close': 'rsie'})
                    df = pd.merge(df, rsi_signal, how='left', left_index=True, right_index=True)
                    #df.to_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/df_rsi_out.csv")

    return df_screener





    # Set the directories
    # Loop for all the approaches
    for i in approach:
        # BB Approach
        if i == "BB":
            # Loop for all the methods
            for j in methods:
                # Buy & Sell
                if j == "BPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str1/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str1/train/sell/"
                    for k in range(20,len(df.bb_signal)):
                        if df.bb_signal[k] != 0:
                            # plotgraph(start, finish, method,approach,str_dir_1, str_dir_2):
                            plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
                # Buy and [Hold + Sell]
                elif j == "BHPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str2/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str2/train/hold_sell/"
                    for k in range(20, len(df.bb_signal)):
                        plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
                # [Buy + Hold], Sell
                else:
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str3/train/buy_hold/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str3/train/sell/"
                    for k in range(20, len(df.bb_signal)):
                        plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
        # RSI Approach
        else:
            # Loop for all the methods
            for j in methods:
                # Buy & Sell
                if j == "BPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str1/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str1/train/sell/"
                    for k in range(14,len(df.rsie)):
                        if ((df.rsie[k] < 30) | (df.rsie[k] >70)):
                            plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)
                # Buy and [Hold + Sell]
                elif j == "BHPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str2/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str2/train/hold_sell/"
                    for k in range(14,len(df.rsie)):
                        plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)
                # [Buy + Hold], Sell
                else:
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str3/train/buy_hold/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str3/train/sell/"
                    for k in range(14,len(df.rsie)):
                        plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)






    # Get the current working directory
    cwd = os.getcwd()
    print(cwd)
    os.chdir('../')
    os.chdir('../')
    os.chdir('../')
    cwd = os.getcwd()
    print(cwd)
    # Parameters
    root_dir = cwd
    #root_dir = "C:\Users\despo\PycharmProjects"
    approach = ['BB','RSI']
    methods = ['BPS','BHPS','BPHS']
    str_dir_1 = str()
    str_dir_2 = str()

    # Pull data from yahoo with a timeline from 1983 1st Jan to - 2021 17th June
    ticker = '^GSPC'

    toto = True
    if toto == False:
        df = yf.download(ticker, start='1983-01-01', end='2021-06-20')
        df.reset_index(inplace=True)

    startdate = '1983-01-01'
    enddate = '2021-06-20'
    # startdate = "2000-01-01"
    # enddate = "2021-01-01"

    #ticker = df.index.tolist()[0][1]

    data = get_data(ticker, start_date=startdate, end_date=enddate)
    data['date'] = data.index
    #data.reset_index(inplace=True)
    data.reset_index(drop=True, inplace=True)

    for column in data.columns:
        is_in = 0
        for data_column in ['date','open','high','low','close','adjclose','volume']:
            if column == data_column:
                is_in = 1
        if is_in == 0:
            data = data.drop([column], axis=1)

    column_names = ['date','open','high','low','close','adjclose','volume']
    data = data.reindex(columns=column_names)

    df = pd.DataFrame()
    df['Date'] = data['date'].copy()
    df['Open'] = data['open'].copy()
    df.Open = df.Open.round(2)
    df['High'] = data['high'].copy()
    df.High = df.High.round(2)
    df['Low'] = data['low'].copy()
    df.Low = df.Low.round(2)
    df['Close'] = data['close'].copy()
    df.Close = df.Close.round(2)
    df['Adj Close'] = data['adjclose'].copy()
    df['Adj Close'] = df['Adj Close'].round(2)
    df['Volume'] = data['volume'].copy()
    df.reset_index(drop=True, inplace=True)

    # Save the raw file to CSV
    df.to_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/stock_data.csv",index=False)

    # Import the scraped data
    df = pd.read_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/stock_data.csv")

    df = df[['Date','Open','High','Low','Close']]
    df = df.rename({'Date':'date','High':'high','Low':'low','Open':'open','Close':'close'},axis=1)
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index)

    # Bollinger Bands calculation

    # Moving Averages Calculation
    def sma(data, window):
        sma = data.rolling(window = window).mean()
        return sma
    df['sma_20'] = sma(df['close'], 20)

    # Bands Calculation
    def bb(data, sma, window):
        std = data.rolling(window = window).std()
        upper_bb = sma + std * 2
        lower_bb = sma - std * 2
        return upper_bb, lower_bb
    df['upper_bb'], df['lower_bb'] = bb(df['close'], df['sma_20'], 20)

    # Function for bb strategy
    def implement_bb_approach(data, lower_bb, upper_bb):
        bb_signal = []
        for i in range(len(data)):
            # Two consecutive rows comparison for trend detection
            # Scenario 1 Both Below Lower Band - Buy
            if data[i - 1] < lower_bb[i - 1] and data[i] < lower_bb[i]:
                signal = 1
                bb_signal.append(signal)
            # Scenario 2 Middle to Upper - Sell
            elif data[i - 1] < upper_bb[i - 1] and data[i] > upper_bb[i]:
                signal = -1
                bb_signal.append(signal)
            # Scenario 3 Both Upper - Sell
            elif data[i - 1] > upper_bb[i - 1] and data[i] > upper_bb[i]:
                signal = -1
                bb_signal.append(signal)
            # Scenario 4 Middle to Lower - Buy
            elif data[i - 1] > lower_bb[i - 1] and data[i] < lower_bb[i]:
                signal = 1
                bb_signal.append(signal)
            else:
                bb_signal.append(0)

        return bb_signal

    def implement_rsi_approach(close, window):

        # Price increase or decrease over previous day
        dif = close.diff()
        dif = dif[1:]

        # pos_m identifies stock price going up
        # neg_m udentifies stock price going down
        pos_m, neg_m = dif.copy(), dif.copy()
        pos_m[pos_m < 0] = 0
        neg_m[neg_m > 0] = 0

        # Positive Rolling Mean Exponential
        prme = pos_m.ewm(span=window).mean()
        # Negative Rolling Mean Exponential
        nrme = neg_m.abs().ewm(span=window).mean()

        # Ratio of magnitude of up move to down move
        RSE = prme / nrme
        RSIE = 100.0 - (100.0 / (1.0 + RSE))
        return RSIE

    # Signal Generation wrt bands
    for i in approach:
        # BB
        if i == "BB":
            bb_signal = implement_bb_approach(df['close'], df['lower_bb'], df['upper_bb'])
            bb_signal = pd.DataFrame(bb_signal).rename(columns = {0:'bb_signal'}).set_index(df.index)
            df = df.join(bb_signal, how = 'inner')
            df.reset_index(inplace=True)
            df.to_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/df_bb_out.csv")
            print(df.bb_signal.value_counts(dropna=False))
        # RSI
        else:
            rsi_signal = implement_rsi_approach(df['close'], 14)
            rsi_signal = pd.DataFrame(rsi_signal).rename(columns={'close': 'rsie'})
            df = pd.merge(df, rsi_signal, how='left', left_index=True, right_index=True)
            df.to_csv(root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/data/df_rsi_out.csv")


    # Creating Images
    def plotgraph(start,finish,method,approach,str_dir_1,str_dir_2):
        open = []
        high = []
        low = []
        close = []
        # Get the data from the dataframe
        for x in range(finish - start):
            open.append(float(df.iloc[start][1]))
            high.append(float(df.iloc[start][2]))
            low.append(float(df.iloc[start][3]))
            close.append(float(df.iloc[start][4]))
            start = start + 1
        fig = plt.figure(num=1, figsize=(3, 3), dpi=50, facecolor='w', edgecolor='k')
        dx = fig.add_subplot(111)
        mpl_finance.candlestick2_ochl(dx, open, close, high, low, width=1.5, colorup='g', colordown='r', alpha=0.5)
        plt.autoscale()
        plt.axis('off')

        # BB Approach
        if approach == "BB":
            # Save to separate directories
            if method == "BPS":
            # Buy & Sell
                if df.bb_signal[finish] == 1:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight') #buy
                else:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight') #sell
            # Buy , [Hold + Sell]
            elif method == "BHPS":
                if df.bb_signal[finish] == 1:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight') #buy
                else:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight') #sell + hold
            #[Buy + Hold], Sell
            else:
                if df.bb_signal[finish] == -1:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight') #sell
                else:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight') #buy + hold

        # RSI Approach
        else:
            # Save to separate directories
            if method == "BPS":
                # Buy(<30) & Sell(>70)
                if df.rsie[finish] < 30:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight')  # buy
                else:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight')  # sell

            # Buy(<30) , [Hold + Sell](>=30)
            elif method == "BHPS":
                if df.rsie[finish] < 30:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight')  # buy
                else:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight')  # sell + hold

            # [Buy + Hold](<=70), Sell(>70)
            else:
                if df.rsie[finish] >70:
                    plt.savefig(str_dir_2 + str(finish) + '.jpg', bbox_inches='tight')  # sell
                else:
                    plt.savefig(str_dir_1 + str(finish) + '.jpg', bbox_inches='tight')  # buy + hold


        open.clear()
        high.clear()
        low.clear()
        close.clear()
        plt.cla()
        plt.clf()

    # Set the directories
    # Loop for all the approaches
    for i in approach:
        # BB Approach
        if i == "BB":
            # Loop for all the methods
            for j in methods:
                # Buy & Sell
                if j == "BPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str1/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str1/train/sell/"
                    for k in range(20,len(df.bb_signal)):
                        if df.bb_signal[k] != 0:
                            # plotgraph(start, finish, method,approach,str_dir_1, str_dir_2):
                            plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
                # Buy and [Hold + Sell]
                elif j == "BHPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str2/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str2/train/hold_sell/"
                    for k in range(20, len(df.bb_signal)):
                        plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
                # [Buy + Hold], Sell
                else:
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str3/train/buy_hold/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/bb/str3/train/sell/"
                    for k in range(20, len(df.bb_signal)):
                        plotgraph(k - 20, k,j,i,str_dir_1, str_dir_2)
        # RSI Approach
        else:
            # Loop for all the methods
            for j in methods:
                # Buy & Sell
                if j == "BPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str1/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str1/train/sell/"
                    for k in range(14,len(df.rsie)):
                        if ((df.rsie[k] < 30) | (df.rsie[k] >70)):
                            plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)
                # Buy and [Hold + Sell]
                elif j == "BHPS":
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str2/train/buy/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str2/train/hold_sell/"
                    for k in range(14,len(df.rsie)):
                        plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)
                # [Buy + Hold], Sell
                else:
                    str_dir_1 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str3/train/buy_hold/"
                    str_dir_2 = root_dir + "/Image-Classification-for-Trading-Strategies/stockpred/rsi/str3/train/sell/"
                    for k in range(14,len(df.rsie)):
                        plotgraph(k-14,k,j,i,str_dir_1, str_dir_2)
