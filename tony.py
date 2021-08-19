#!/usr/bin/python3.7
"""
Created on Wed May  5 15:34:13 2021

@author: Orhan
"""

import websocket, json, talib, numpy
import config
from binance.client import Client
from binance.enums import *
from datetime import datetime, date, timedelta
import pandas as pd
from find_RSI_parameters import find_RSI_parameters

client = Client(config.API_KEY, config.API_SECRET)

###############################################################################
# Select the Values

in_position = False
select_options = False

price = 0
quantity = 100

TRADE_SYMBOL = 'MATICEUR'

start_date = (date.today()-timedelta(days=1)).strftime("%Y-%m-%d")
end_date = (date.today()+timedelta(days=1)).strftime("%Y-%m-%d")
_start_date = (date.today()-timedelta(days=1)).strftime("%d %B, %Y")
_end_date = (date.today()+timedelta(days=1)).strftime("%d %B, %Y")

###############################################################################

# RSI_OVERBOUGHT = 97.5
# RSI_OVERSOLD = 5
RSI_PERIOD = 3

candlesticks = client.get_historical_klines(TRADE_SYMBOL,
                                            Client.KLINE_INTERVAL_30MINUTE,
                                            _start_date, _end_date)
candlesticks = candlesticks[-96:]

unit = 30
timing = 'm'
SOCKET = "wss://stream.binance.com:9443/ws/{0}@kline_{1}{2}".format(TRADE_SYMBOL.lower(),
                                                                    unit, timing)
###############################################################################

if in_position and not select_options:
    paid_price = float(client.get_my_trades(symbol=TRADE_SYMBOL)[-1]['price'])
    TRADE_QUANTITY = float(client.get_my_trades(symbol=TRADE_SYMBOL)[-1]['qty'])

elif in_position and select_options:
    paid_price = price
    TRADE_QUANTITY = quantity

elif not in_position:
    paid_price = 0
    TRADE_QUANTITY = quantity

results = find_RSI_parameters(TRADE_SYMBOL, TRADE_QUANTITY, start_date, end_date)
RSI_OVERBOUGHT = round(results['params']['y'], 2)
RSI_OVERSOLD = round(results['params']['x'], 2)
print(results)

###############################################################################

closes = []
df = pd.DataFrame(candlesticks)
closes = df[:][4].to_list()[0:-1]
closes = list(map(float, closes))

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position, paid_price, results, TRADE_QUANTITY
    global RSI_OVERBOUGHT, RSI_OVERSOLD

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time = {0}. Received message for {1}".format(current_time, TRADE_SYMBOL))

    json_message = json.loads(message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print('\n')
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes[-10:])

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print('\n')
            print("all rsis calculated so far")
            print(rsi[-10:])
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))
            print('\n')

            if last_rsi > RSI_OVERBOUGHT and closes[-1] > 0 :
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False

                        paid_price = 0
                        TRADE_QUANTITY = float(client.get_my_trades(symbol=TRADE_SYMBOL)[-1]['qty'])
                        TRADE_QUANTITY = TRADE_QUANTITY - int(TRADE_QUANTITY*0.002)

                    else:
                        print("Something is wrong during selling. FIX ME!!!\n")
                        return
                else:
                    print("It is overbought, but we don't own any. Nothing to do.\n")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.\n")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
                        paid_price = float(client.get_my_trades(symbol=TRADE_SYMBOL)[-1]['price'])
                    else:
                        print("Something is wrong during buying. FIX ME!!!\n")
                        return

        now = datetime.now().time()
        current_str = now.strftime("%H:%M")
        current_hour = int(current_str[0:2])
        current_minute = int(current_str[3:5])
        check_time_minute = current_minute%60
        check_time_hour = current_hour%4

        if check_time_hour == 0 and check_time_minute == 5:
            start_date = (date.today()-timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = (date.today()+timedelta(days=1)).strftime("%Y-%m-%d")
            _start_date = (date.today()-timedelta(days=1)).strftime("%d %B, %Y")
            _end_date = (date.today()+timedelta(days=1)).strftime("%d %B, %Y")

            results = find_RSI_parameters(TRADE_SYMBOL, TRADE_QUANTITY, start_date, end_date)
            RSI_OVERBOUGHT = round(results['params']['y'], 2)
            RSI_OVERSOLD = round(results['params']['x'], 2)
            print('\n')
            print(results)

        print('\n')



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

