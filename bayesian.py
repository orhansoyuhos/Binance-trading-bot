#!/usr/bin/python3.7
"""
Created on Tue May  4 23:39:36 2021

@author: Orhan
"""
#https://github.com/fmfn/BayesianOptimization


from bayes_opt import BayesianOptimization

import backtrader as bt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time

start_time = time.monotonic()


class RSIStrategy(bt.Strategy):

    def __init__(self, x, y):
        self.rsi = bt.talib.RSI(self.data, timeperiod=3)
        self.x = x
        self.y = y

    def next(self):
        if self.rsi < self.x and not self.position:
            self.buy(size=2000)

        if self.rsi > self.y and self.position:
            self.close()

def black_box_function(x, y):

    fromdate = datetime.datetime.strptime('2021-06-01', '%Y-%m-%d')
    todate = datetime.datetime.strptime('2021-06-18', '%Y-%m-%d')
    data = bt.feeds.GenericCSVData(dataname='DOGEUSDT_5min_test.csv', dtformat=2,
                                   compression=5, timeframe=bt.TimeFrame.Minutes,
                                   fromdate=fromdate, todate=todate)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000.0)
    cerebro.adddata(data)
    cerebro.addstrategy(RSIStrategy, x, y)
    cerebro.run()

    return cerebro.broker.getvalue()

# x: low, y: high

# Bounded region of parameter space
pbounds = {'x': (1, 50), 'y': (50, 99)}

optimizer = BayesianOptimization(
    f = black_box_function,
    pbounds = pbounds,
    random_state = 1,
)

optimizer.maximize(
    init_points = 10,
    n_iter = 100,
)

print(optimizer.max)

# for i, res in enumerate(optimizer.res):
#     print("Iteration {}: \n\t{}".format(i, res))

print('seconds: ', time.monotonic() - start_time)
