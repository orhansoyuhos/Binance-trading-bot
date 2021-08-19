#!/usr/bin/python3.7
"""
Created on Tue May  4 00:19:12 2021

@author: Orhan
"""
# do not forget to change Client.KLINE_INTERVAL_15MINUTE !!!!

import config, csv
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

# prices = client.get_all_tickers()

# for price in prices:
#     print(price)

csvfile = open('DOGEUSDT_5min_test.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')
candlesticks = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_5MINUTE,
                                            "1 June, 2021", "18 June, 2021")

# csvfile = open('DOGEEUR_1min.csv', 'w', newline='')
# candlestick_writer = csv.writer(csvfile, delimiter=',')
# candlesticks = client.get_historical_klines("DOGEEUR", Client.KLINE_INTERVAL_1MINUTE, "1 May, 2021", "4 May, 2021")

# csvfile = open('DOGEEUR_3min.csv', 'w', newline='')
# candlestick_writer = csv.writer(csvfile, delimiter=',')
# candlesticks = client.get_historical_klines("DOGEEUR", Client.KLINE_INTERVAL_3MINUTE, "1 May, 2021", "4 May, 2021")

# csvfile = open('DOGEEUR_15min.csv', 'w', newline='')
# candlestick_writer = csv.writer(csvfile, delimiter=',')
# candlesticks = client.get_historical_klines("DOGEEUR", Client.KLINE_INTERVAL_15MINUTE, "1 May, 2021", "4 May, 2021")

# csvfile = open('DOGEEUR_1hour.csv', 'w', newline='')
# candlestick_writer = csv.writer(csvfile, delimiter=',')
# candlesticks = client.get_historical_klines("DOGEEUR", Client.KLINE_INTERVAL_1HOUR, "1 May, 2021", "4 May, 2021")

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