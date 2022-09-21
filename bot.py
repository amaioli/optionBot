from utils import minimumOrder
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pytz
import time
from deribit import Deribit
from notifier import Notifier


class Bot:
    '''
    Bot class
    '''

    def __init__(self, config, exchange: Deribit, notifier: Notifier) -> None:
        self.positions = []
        self.currency = config['strategy']["currency"]
        self.contractSize = float(config['strategy']["contractSize"])
        self.targetDelta = float(config['strategy']["targetDelta"])
        self.optionSides = config['strategy']["optionSides"]
        self.optionSettlement = config['strategy']["optionSettlement"]
        self.hedging = config['strategy']["hedging"]
        self.hedgingThreshold = float(config['strategy']["hedgingThreshold"])
        self.orderType = config['strategy']["orderType"]
        self.exchange = exchange
        self.compounding = config['strategy']["compounding"]
        # self.sched = BackgroundScheduler()
        # self.sched.daemonic = False
        # self.sched.timezone = pytz.utc
        self.notifier = notifier

    def start(self):
        self.slotTimeHandler()
        # self.sched.add_job(self.slotTimeHandler, 'cron', minute=30)
        # self.sched.start()
        # while True:
        #     time.sleep(10)

    def stop(self):
        self.exchange.cancelOrders(self.currency)
        # self.sched.shutdown()
        pass

    def slotTimeHandler(self):
        # CANCEL OLD PENDING ORDERS
        self.exchange.cancelOrders(self.currency)

        # MANAGE POSITIONS
        for optionType in ['put', 'call']:
            if optionType in self.optionSides:
                size = self.exchange.fetchOptionPositions(
                    optionType, self.currency)
                if size < self.contractSize:

                    instrument = self.exchange.findOption(
                        self.currency, optionType, self.optionSettlement, self.targetDelta)
                    if self.contractSize - size >= minimumOrder(self.currency) and instrument:
                        # ADD POSITION
                        self.exchange.addPosition(
                            instrument, self.orderType, 'sell', self.contractSize - size)
                        self.notifier.send(f'Added {instrument} order with size {str(self.contractSize - size)}')
                    else:
                        logging.warning(
                            f'Not found option {optionType} matching the target delta')

        # INTRADAY HEDGING SECTION
        delta = self.exchange.portfoglioDelta(self.currency)
        logging.warning(f'Current Delta: {str(delta)}')
        if abs(delta) > self.hedgingThreshold:
            self.exchange.portfoglioHedge(self.hedgingThreshold, self.currency)
            self.notifier.send(f'Hedging delta: {delta} {self.currency}')
