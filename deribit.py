import ccxt
import requests
import json
from utils import priceRounding
import logging

class Deribit():
    def __init__(self, key, secret):
        self._client = ccxt.deribit({"apiKey": key, "secret": secret})
        self._client.load_markets(reload=True)

    def findOption(self, base: str, optionType: str, settlementPeriod: str, delta: float):
        '''
        Find the Instrument that meet the parameters
        '''
        self._client.load_markets(reload=True)

        # Build a list of instrument filtered and ordered based on parameters
        v = 1 if optionType == 'call' else -1

        # For daily option strategy select also in the week expiration options
        settlementPeriod = ('day', 'week', 'month') if settlementPeriod == 'day' else settlementPeriod

        market_list = sorted([ins for ins in self._client.markets.values() if
                              ins["base"] == base and
                              ins["optionType"] == optionType and
                              ins["info"]["kind"] == 'option' and
                              ins["info"]["settlement_period"] in settlementPeriod and
                              ins["info"]["is_active"] == True], key=lambda k: (k['expiry'], v*k['strike']))

        # Return the first instrument with delta below the parameter
        for i in market_list:

            orderBook = self._getOrderBook(i['id'])
            if abs(float(orderBook['greeks']['delta'])) > delta:
                continue

            return i['id']

        return None

    def addPosition(self, instrument: str, orderType: str, side: str, size: float):
        '''
        Add position 
        params: side: 'buy' or 'sell'
        params: instrument: ie. BTC-PERPETUAL
        params: orderType: 'maker' or 'taker'
        params: size
        '''
        orderBook = self._getOrderBook(instrument)
        best_bid_price = float(orderBook['best_bid_price'])
        best_ask_price = float(orderBook['best_ask_price'])
        price = priceRounding(
            best_bid_price, best_ask_price, instrument[0:3], 'maker')

        if orderType == 'taker':

            price = size * price if 'PERPETUAL' in instrument else size
            logging.warning(
                f'Added market order of {instrument} with size {size}')
            self._client.create_order(
                symbol=instrument, type='market', side=side, amount=price)

        elif orderType == 'maker':

            logging.warning(
                f'Added limit order of {instrument} with size {size} and price {price}')
            self._client.create_order(
                instrument, 'limit', side, float(size), price)

    def cancelOrders(self, currency: str):

        r = self._client.fetch_open_orders()

        for ord in r:
            if currency in ord['symbol']:
                self._client.cancel_order(ord['id'])

    def portfoglioDelta(self, currency: str):
        '''
        Get the portfoglio delta
        params: currency: 'BTC', 'ETH' or 'SOL'
        '''

        r = self._client.fetch_balance({'currency': currency})

        return float(r['info']['delta_total'])

    def fetchOptionPositions(self, optionType: str, currency: str, side: str = 'short'):
        '''
        fetch size of options used by the strategy
        :params: optionType: 'put' or 'call'
        :params: currency: 'BTC, 'ETH' or 'SOL'
        :params: side: 'buy' or 'sell'
        '''

        side = 'sell' if side == 'short' else 'buy'

        positions = self._client.fetchPositions(params = {'currency': currency, 'kind': 'option'})

        optionType = '-C' if optionType == 'call' else '-P'

        total_position = 0
        instrumentName = ""
        unPnl = 0

        for pos in positions:
            if (currency in pos['info']['instrument_name']) and (optionType in pos['info']['instrument_name']) and pos['info']['kind'] == 'option' and pos['info']['direction'] == side:
                total_position = total_position + \
                    abs(float(pos['info']['size']))
                instrumentName = pos['info']['instrument_name']
                orderBook = self._getOrderBook(instrumentName)
                best_bid_price = float(orderBook['best_bid_price'])
                best_ask_price = float(orderBook['best_ask_price'])
                unPnl = ((- best_ask_price + pos['entryPrice']) / pos['entryPrice']) if side == 'sell' else ((best_bid_price - pos['entryPrice']) / pos['entryPrice'])

        return total_position, instrumentName, unPnl

    def portfoglioHedge(self, hedgingThreshold: float, currency: str):
        '''
        Bring Hedge to the target value
        params: currency: 'BTC', 'ETH' or 'SOL'
        '''

        deltaCurrent = self.portfoglioDelta(currency)
        side = 'sell' if deltaCurrent > 0 else 'buy'

        if abs(deltaCurrent) > hedgingThreshold:

            self.addPosition(currency + "-PERPETUAL",
                             'taker', side, abs(deltaCurrent))

    def _getOrderBook(self, instrument_name, depth=1):

        url = "/api/v2/public/get_order_book"
        parameters = {'instrument_name': instrument_name,
                      'depth': depth}
        # send HTTPS GET request
        json_response = requests.get(
            ("https://www.deribit.com" + url + "?"), params=parameters)
        response_dict = json.loads(json_response.content)
        order_book = response_dict["result"]

        return order_book
