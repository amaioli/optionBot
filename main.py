from bot import Bot
import signal
import configparser
from deribit import Deribit
from notifier import Notifier
import logging
import time
import pytz
import glob
from apscheduler.schedulers.background import BackgroundScheduler


def handler(signum, frame):
    # bot.stop()
    sched.remove_all_jobs()
    sched.shutdown()
    exit(1)


signal.signal(signal.SIGINT, handler)

config = configparser.ConfigParser()
# config.read("./config/config.ini")

logging.getLogger().setLevel(logging.WARNING)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

# Bots scheduler creation
sched = BackgroundScheduler()
sched.timezone = pytz.utc
sched.daemonic = False

for config_file in glob.glob("./config/*.ini"):
    config.read(config_file)
    # TODO config validator
    print(type(config))

    # Instantiace exchange connector
    deribit = Deribit(config['DERIBIT']["key"], config['DERIBIT']["secret"])
    deribit.enableRateLimit = True

    # Instantiace notifier
    notifier = Notifier(
        config['NOTIFICATION']["telegramChatId"], config['NOTIFICATION']["alias"])

    # Instantiace bot
    bot = Bot(currency=config['STRATEGY']["currency"],
              contractSize=config['STRATEGY']["contractSize"],
              compounding=config['STRATEGY']["compounding"],
              targetDelta=config['STRATEGY']["targetDelta"],
              optionSides=config['STRATEGY']["optionSides"],
              optionSettlement=config['STRATEGY']["optionSettlement"],
              hedging=config['STRATEGY']["hedging"],
              hedgingThreshold=config['STRATEGY']["hedgingThreshold"],
              orderType=config['STRATEGY']["orderType"],
              exchange=deribit,
              notifier=notifier)

    sched.add_job(bot.start, 'cron', minute=15)
    notifier.send('Bot started')

sched.start()

while True:
    time.sleep(10)
