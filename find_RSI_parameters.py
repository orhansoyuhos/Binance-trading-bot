#!/usr/bin/python3.7
"""
Created on Fri May  7 00:48:22 2021

@author: Orhan
"""
import config, csv
from binance.client import Client
from bayes_opt import BayesianOptimization
import backtrader as bt


def find_RSI_parameters(TRADE_SYMBOL, TRADE_QUANTITY, start_date, end_date, cash=100.0):

    def black_box_function(x, y):

        class RSIStrategy(bt.Strategy):

            def __init__(self, x, y, TRADE_QUANTITY):
                self.rsi = bt.talib.RSI(self.data, timeperiod=3)
                self.x = x
                self.y = y
                self.TRADE_QUANTITY = TRADE_QUANTITY

            def next(self):
                if self.rsi < self.x and not self.position:
                    self.buy(size=self.TRADE_QUANTITY)

                if self.rsi > self.y and self.position:
                    self.close()

        data = bt.feeds.GenericCSVData(dataname='{0}_30min.csv'.format(TRADE_SYMBOL),
                                       dtformat=2, compression=30,
                                       timeframe=bt.TimeFrame.Minutes)

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(cash)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategy, x, y, TRADE_QUANTITY)
        cerebro.run()

        return cerebro.broker.getvalue()

    # PART 1
    client = Client(config.API_KEY, config.API_SECRET)

    csvfile = open('{0}_30min.csv'.format(TRADE_SYMBOL), 'w', newline='')
    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_30MINUTE,
                                                start_date, end_date)

    candlesticks = candlesticks[-96:]

    features = ["Open time", "Open", "High", "Low", "Close", "Volume",
                "Close time", "Quote asset volume", "Number of trades",
                "Taker buy base asset volume", "Taker buy quote asset volume",
                "Ignore"]
    writer = csv.DictWriter(
        csvfile, fieldnames=features)
    writer.writeheader()
    for candlestick in  candlesticks:
        candlestick[0] = candlestick[0] / 1000
        candlestick_writer.writerow(candlestick)
    csvfile.close()

    # PART 2
    # black_box = lambda x, y: black_box_function(x, y, TRADE_SYMBOL, TRADE_QUANTITY, cash=cash)

    pbounds = {'x': (1, 40), 'y': (60, 99)}

    optimizer = BayesianOptimization(
        f = black_box_function,
        pbounds = pbounds,
        random_state = 1, verbose=1
    )
    optimizer.maximize(
        init_points = 5,
        n_iter = 100,
    )

    return optimizer.max
