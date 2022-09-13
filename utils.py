import datetime

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)*24):
        yield start_date + datetime.timedelta(hours=n)

def checkSettlementTime(time:datetime, optionSettlement:str):
    '''
    Check if time is in the range of Settment time (Friday from 6.59 to 9.00 UTC)
    '''
    if optionSettlement == "week":
        settlementList = [4]
    elif optionSettlement == "day":
        settlementList = [0,1,2,3,4,5,6,7]
    if (time.weekday() in settlementList) and time.time() < datetime.time(9,0,0,0) and time.time() > datetime.time(6,59,0,0):
        return True
    return False

def fee(type:str, size: float, settlementPeriod: str, price: float = 0):
    if type == 'option':
        # Acquisition fee
        fee = size * 0.03 / 100 if size * 0.03 / 100 > 0.0003 else 0.0003
        fee = price * size * 12.5 / 100 if fee > price * size * 12.5 / 100 else fee
        # Delivery fee for weekly and montly options
        if settlementPeriod != 'day':
            fee = fee + size * 0.015 / 100 if size * 0.015 / 100 < price * size * 12.5 / 100 else fee + price * size * 12.5 / 100
    elif type == 'future':
        fee = size * 0.05 / 100

    return fee

def minimumOrder(currency: str) -> float:
    if currency in ['BTC', 'ETH']:
        return 0.1
    else:
        return 1

def priceRounding(bid: float, ask:float, asset:str, orderType:str = 'taker'):
    if orderType == 'taker':
        return max(bid, 0.0005) if asset in ('BTC', 'ETH') else max(bid, 0.001)
    if asset in ('BTC', 'ETH'):
        middleRounded = int(((ask + bid) / 2) / 0.0005) * 0.0005
        return max(bid, middleRounded, 0.0005)
    else:
        middleRounded = int(((ask + bid) / 2) / 0.001) * 0.001
        return max(bid, middleRounded, 0.001)


