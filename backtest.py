#!/usr/bin/python3.7
"""
Created on Tue May  4 00:27:16 2021

@author: Orhan
"""

import backtrader as bt
import datetime
import pandas as pd
import matplotlib.pyplot as plt



class RSIStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, timeperiod = 3)

    def next(self):
        if self.rsi < 15 and not self.position:
            self.buy(size = 2000)

        if self.rsi > 95 and self.position:
            self.close()


## 20-96.5 best upward
## 10-60 best downward



fromdate = datetime.datetime.strptime('2021-06-01', '%Y-%m-%d')
todate = datetime.datetime.strptime('2021-06-18', '%Y-%m-%d')
data = bt.feeds.GenericCSVData(dataname='DOGEUSDT_5min_test.csv', dtformat=2, compression=5,
                                timeframe=bt.TimeFrame.Minutes, fromdate=fromdate,
                                todate=todate)

cerebro = bt.Cerebro()
cerebro.broker.setcash(1000.0)
cerebro.adddata(data)
cerebro.addstrategy(RSIStrategy)
cerebro.run()
print(cerebro.broker.getvalue())

# cerebro.plot()
