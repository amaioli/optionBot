# optionBot
A bot managing a strangle selling strategy on Deribit.

# Install

pip install -r requirement.txt

# Configuration parameters

[STRATEGY]
currency = BTC currency to operate with
contractSize = 0.1 options contract size
compounding = False                     
targetDelta = 0.15                      maximum delta during option selling
optionSides = ['put', 'call']           side option selling 
optionSettlement = day                  option settlement period (day, week or month)
hedging = True                          enable the dynamic delta hedging through Future buy/sell
hedgingThreshold = 0.03                 delta threshold to start heding
orderType = taker                       'taker' to sell option on bid book. 'maker' to try selling at middle price
[DERIBIT]
key = xxx
secret = xxxx
[NOTIFICATION]
telegramChatId = xxxx                   Chatid to get notification from Telegram bot (@optionBot_bot)
alias = Main


