from bot import Bot
import signal
import configparser
from deribit import Deribit
import logging


def handler(signum, frame):
    bot.stop()
    exit(1)


signal.signal(signal.SIGINT, handler)

config = configparser.ConfigParser()
config.read("config.ini")

logging.getLogger().setLevel(logging.WARNING)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

# Instantiace exchange connector
deribit = Deribit(config['DERIBIT']["key"], config['DERIBIT']["secret"])

bot = Bot(currency=config['STRATEGY']["currency"],
          contractSize=config['STRATEGY']["contractSize"],
          compounding=config['STRATEGY']["compounding"],
          targetDelta=config['STRATEGY']["targetDelta"],
          optionSides=config['STRATEGY']["optionSides"],
          optionSettlement=config['STRATEGY']["optionSettlement"],
          hedging=config['STRATEGY']["hedging"],
          hedgingThreshold=config['STRATEGY']["hedgingThreshold"],
          orderType=config['STRATEGY']["orderType"],
          exchange=deribit)

bot.start()
