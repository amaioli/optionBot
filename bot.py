from utils import minimumOrder
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import pytz, time
from deribit import Deribit



class Bot:
    '''
    Bot class
    '''

    def __init__(self, currency, contractSize, targetDelta, optionSides, optionSettlement, hedging: bool, hedgingThreshold, orderType, exchange: Deribit, compounding) -> None:
        self.positions = []
        self.currency = currency
        self.contractSize = float(contractSize)
        self.targetDelta = float(targetDelta)
        self.optionSides = optionSides
        self.optionSettlement = optionSettlement
        self.hedging = eval(hedging)
        self.hedgingThreshold = float(hedgingThreshold)
        self.orderType = orderType
        self.exchange = exchange
        self.compounding = compounding
        self.sched = BackgroundScheduler()
        self.sched.daemonic = False
        self.sched.timezone = pytz.utc

    def start(self):
        self.sched.add_job(self.slotTimeHandler, 'cron', minute=1)
        self.sched.start()
        while True:
            time.sleep(10)

    def stop(self):
        self.sched.remove_all_jobs()
        self.sched.shutdown()


    def slotTimeHandler(self):
        # CANCEL OLD PENDING ORDERS
        self.exchange.cancelOrders(self.currency)

        # MANAGE POSITIONS
        for optionType in ['put', 'call']:
            if optionType in self.optionSides:
                size = self.exchange.fetchOptionPositions(optionType, self.currency)
                if size < self.contractSize:

                    instrument = self.exchange.findOption(self.currency, optionType, self.optionSettlement, self.targetDelta)
                    if self.contractSize - size >= minimumOrder(self.currency) and instrument:
                        # ADD POSITION
                        self.exchange.addPosition(instrument, self.orderType,'sell', self.contractSize - size)
                    else:
                        logging.warning(f'Not found option {optionType} matching the target delta')


        # INTRADAY HEDGING SECTION
        delta = self.exchange.portfoglioDelta(self.currency)
        logging.warning(f'Current Delta: {str(delta)}')
        if abs(delta) > self.hedgingThreshold:
            self.exchange.portfoglioHedge(self.hedgingThreshold, self.currency)
