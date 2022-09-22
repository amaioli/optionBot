from bot import Bot
import signal
from deribit import Deribit
from notifier import Notifier
import logging
import time
import pytz
import glob
from apscheduler.schedulers.background import BackgroundScheduler
from utils import configParserYaml



def handler(signum, frame):
    bot.stop()
    sched.remove_all_jobs()
    sched.shutdown()
    exit(1)


if __name__ == '__main__':

    # Register signal handler
    signal.signal(signal.SIGINT, handler)

    # Configuring logging
    logging.getLogger().setLevel(logging.WARNING)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT)

    # Bots scheduler creation
    sched = BackgroundScheduler()
    sched.timezone = pytz.utc
    sched.daemonic = False


    for config_file in glob.glob("./config/*.yaml"):

        # Validation and loading config
        config = configParserYaml(config_file)

        # Instantiace exchange connector
        deribit = Deribit(config['deribit']["key"], config['deribit']["secret"])
        deribit.enableRateLimit = True

        # Instantiace notifier
        notifier = Notifier(
            config['notification']["telegramChatId"], config['notification']["alias"])

        # Instantiace bot
        bot = Bot(config = config, exchange=deribit, notifier=notifier)

        sched.add_job(bot.start, 'cron', minute=10)
        notifier.send(f'Bot started with config {config_file}')

    sched.start()

    while True:
        time.sleep(10)
