"""
# https://towardsdatascience.com/parse-thousands-of-stock-recommendations-in-minutes-with-python-6e3e562f156d
"""

import requests
import pandas as pd
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
import numpy as np

import requests
import re
import json

def get_rating_perfo(df_screener):


    r = requests.get("https://finance.yahoo.com/quote/BABA/analysis?p=BABA")

    toto = re.search('root\.App\.main\s*=\s*(.*);', r.text)

    data = json.loads(re.search('root\.App\.main\s*=\s*(.*);', r.text).group(1))

    field = [t for t in data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["earningsTrend"]["trend"] if t["period"] == "+5y"][0]

    print(field)
    print("Next 5 Years (per annum) : " + field["growth"]["fmt"])





    tickers = si.tickers_sp500()
    recommendations = []

    for ticker in tickers:

        # https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch
        # https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch

        lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
        rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                  'modules=upgradeDowngradeHistory,recommendationTrend,' \
                  'financialData,earningsHistory,earningsTrend,industryTrend&' \
                  'corsDomain=finance.yahoo.com'
        AAPL_url_quote = 'https://finance.yahoo.com/quote/AAPL?p=AAPL'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = lhs_url + ticker + rhs_url
        # r = requests.get(url, headers=headers)

        r = requests.get(AAPL_url_quote, headers=headers)

        if not r.ok:
            recommendation = 6
        try:
            result = r.json()['quoteSummary']['result'][0]
            recommendation = result['financialData']['recommendationMean']['fmt']
        except:
            recommendation = 6

        recommendations.append(recommendation)

        print("--------------------------------------------")
        print("{} has an average recommendation of: ".format(ticker), recommendation)
        # time.sleep(0.5)

    dataframe = pd.DataFrame(list(zip(tickers, recommendations)), columns=['Company', 'Recommendations'])
    dataframe = dataframe.set_index('Company')
    dataframe.to_csv('recommendations.csv')

    print(dataframe)