from utils import minimumOrder
import logging
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
        self.rolling = config['strategy']["rolling"]
        self.rollingTargetProfit = float(config['strategy']["rollingTargetProfit"])
        self.orderType = config['strategy']["orderType"]
        self.exchange = exchange
        self.compounding = config['strategy']["compounding"]
        self.notifier = notifier

    def start(self):
        self.slotTimeHandler()


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
                position = self.exchange.fetchOptionPositions(
                    optionType, self.currency)
                size = position[0]
                instrumentName = position[1]
                unPnl = position[2]
                logging.warning(
                            f'Instrument {instrumentName} Pnl {unPnl}')

                if self.rolling and instrumentName and unPnl > self.rollingTargetProfit:
                    # MANAGE ROLLING
                    self.exchange.addPosition(instrumentName, 'taker', 'buy', size)
                    self.notifier.send(f'Rolling {instrumentName} order with size {str(size)}')

                if size < self.contractSize:
                    # BUILD POSITIONS
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


        # INTRACYCLE HEDGING MANAGEMENT
        delta = self.exchange.portfoglioDelta(self.currency)
        logging.warning(f'Current Delta: {str(delta)}')
        if self.hedging and abs(delta) > self.hedgingThreshold:
            self.exchange.portfoglioHedge(self.hedgingThreshold, self.currency)
            self.notifier.send(f'Hedging delta: {delta} {self.currency}')

