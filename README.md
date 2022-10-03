# optionBot
A bot managing a strangle selling strategy on Deribit.

# Install

pip install -r requirements.txt

# Configuration parameters

| STRATEGY | Value | Desciption |
| --- | --- |--- |
| currency | BTC, ETH or SOL  |currency to operate with |
| contractSize  | float (i.e. 0.1) |options contract size |
| compounding   |  |not still used |
| targetDelta   | float (i.e. 0.15)  |maximum delta during option selling |
| optionSides    | list [‘put’, ‘call’]  |side option selling |
| optionSettlement     | day, week or month  |option settlement period |
| hedging      | True or False |enable the dynamic delta hedging through Future buy/sell |
| hedgingThreshold       | float (i.e. 0.03) |delta threshold to start heding |
| rolling      | True or False |enable the rolling of position in profit |
| rollingTargetProfit       | float 0-1 range (i.e. 0.80) |profit percentage to start rolling |
| orderType       | taker or maker |‘taker’ to sell option on bid book. ‘maker’ to try selling at middle price |

| NOTIFICATION | Value | Desciption |
| --- | --- |--- |
| telegramChatId  | string  |Chatid to get notification from Telegram bot (@optionBot_bot) |
| alias   | string (optional)  |string prefix on chat message |

# Starting

python3 main.py


