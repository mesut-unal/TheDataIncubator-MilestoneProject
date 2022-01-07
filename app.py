import pandas as pd
import json
import requests
import streamlit as st
import plotly.graph_objects as go

import os
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables from .env.

# https://mesutunal-tdimilestoneproject.herokuapp.com/ 

def get_data(curr1,curr2,tint):
    
    load_dotenv()
    env_path = Path('.')/'.env'
    load_dotenv(dotenv_path=env_path)
    SECRET_KEY = os.getenv("SECRET_KEY")

    if tint=='years':
        url = 'https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol='+curr1+'&to_symbol='+curr2+'&apikey='+SECRET_KEY
        tint='Weekly'
    else:
        url = 'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol='+curr1+'&to_symbol='+curr2+'&interval='+tint+'&apikey='+SECRET_KEY

    r = requests.get(url)
    data = r.json()
    
    dfT = pd.DataFrame(data['Time Series FX ('+tint+')'])
    df = dfT.T

    
    return df


def main():
    st.title('Currency Exchange Rates')
    st.subheader('Please choose two currencies you want to compare')

    curr = ['USD','EUR','GBP','TRY','JPY','CNY']
    #currNames = ['United States Dollar','Euro','British Pound Sterling','Turkish Lira','Japanese Yen','Chinese Yuan']
    cN = ["name"]
    others = pd.read_csv('physical_currency_list.csv')

    for i,row in others.iterrows():
        if row['currency code'] not in curr: 
            curr.append(row['currency code'])

    default_ix = curr.index('TRY')

    curr1 = st.selectbox("from", curr)
    curr2 = st.selectbox("to", curr, index=default_ix)

    st.subheader('Please choose the time interval you want to analyze')
    choice = st.selectbox("Time period", ['Last 1 hour','Over the years'], index=0)

    if choice == 'Last 1 hour':
        tint = st.selectbox("Time between each data points",['1min', '5min', '15min', '30min', '60min'], index=4)
    elif choice == 'Over the years':
        tint='years'

    df = get_data(curr1,curr2,tint)

    # clickcnt = 0
    show_button = st.button('Show Chart')
    if show_button:
        col1, col2, col3,col4 = st.columns(4)
        col1.metric("Open", df['1. open'][0])
        col2.metric("Close", df['4. close'][0])
        col3.metric("Low", df['3. low'][0])
        col4.metric("High", df['2. high'][0])

        # clickcnt += 1
        candlestick = go.Candlestick(
                                x=df.index,
                                open=df['1. open'],
                                high=df['2. high'],
                                low=df['3. low'],
                                close=df['4. close']
                                )

        fig = go.Figure(data=[candlestick])
        fig.update_layout(
            width=1000, height=800,
            title=curr1+' / '+curr2+' Over Time',
            yaxis_title=curr1+' / '+curr2
        )

        st.plotly_chart(fig, use_container_width=False)
        # print("clickcnt..............",clickcnt)
        # if clickcnt == 4:
        #     time.sleep(10)
        #     clickcnt = 0

    with st.sidebar:
        st.subheader('The Data Incubator Milestone Project')
        st.write('by M.Unal, January 2022')
        st.write('This is my first project with Streamlit and Heroku. The data are obtained from Alpha Vantage API and Plotly is used for plotting.')

        st.subheader("Currency Symbols")
        others = others.rename(columns={'currency code':'Code  ','currency name':'Name'})
        st.dataframe(others,500,800)

if __name__ == '__main__':
    main()
