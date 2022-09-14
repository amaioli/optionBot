import requests, logging

class Notifier():
    def __init__(self, chatId: str, alias: str):
        self.chatId = chatId
        self.alias = alias

    def send(self, message: str):

        message = f'{self.alias}: {message}'

        url = 'https://api.telegram.org/bot5619010758:AAH1lRQlgHrHnBZ_3bCEazq3vZY7mAd1SHo/sendMessage?chat_id=' + self.chatId +'&text=' + message
        try:
            requests.get(url, timeout=10)
        except:
            logging.warning(f'issue sending Telegram notification')

        