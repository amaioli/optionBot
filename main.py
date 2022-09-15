from bot import Bot
import signal
from deribit import Deribit
from notifier import Notifier
import logging
import time
import pytz
import glob
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from cerberus import Validator
from utils import configParserYaml



def handler(signum, frame):
    # bot.stop()
    sched.remove_all_jobs()
    sched.shutdown()
    exit(1)


signal.signal(signal.SIGINT, handler)

logging.getLogger().setLevel(logging.WARNING)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

# Bots scheduler creation
sched = BackgroundScheduler()
sched.timezone = pytz.utc
sched.daemonic = False


for config_file in glob.glob("./config/*.yaml"):
    # with open(config_file) as f:
    #     try:
    #         config = yaml.load(f, Loader=yaml.FullLoader)
    #     except yaml.YAMLError as exception:
    #         logging.error(f'Invalid yaml config file: {config_file}')
    config = configParserYaml(config_file)

    # Instantiace exchange connector
    deribit = Deribit(config['deribit']["key"], config['deribit']["secret"])
    deribit.enableRateLimit = True

    # Instantiace notifier
    notifier = Notifier(
        config['notification']["telegramChatId"], config['notification']["alias"])

    # Instantiace bot
    bot = Bot(config = config, exchange=deribit, notifier=notifier)

    sched.add_job(bot.start, 'cron', minute=30)
    notifier.send('Bot started')

sched.start()

while True:
    time.sleep(10)
