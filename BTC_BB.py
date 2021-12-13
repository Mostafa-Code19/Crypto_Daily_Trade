import requests, time, json, logging, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx

CryptoToTrade = 'BTC'
timeFrame = '5min'  #1min, 1hour, 1day, 1week
# stopLoseAt = -5  #?change it if you want
waitForNextCheck = 5 * 60  # 5 minute
waitForSell = 60 * 60  # 2 hour
howMuchShouldIBuy = 30  # $
dataOfChart = 'Data/DataForIndicator_BTC_BB.csv'
saveDataHere = 'Trade_Information/orderHistory_BTC_BB.csv'
timePeriodForBB = 20
BBLevelToBuy = 35
orderCounter = 1
access_id = '9AB450BFC9574FF2A081D257A691D556'
secret_key = '1343602FFD3EA564E432286088A534EAEC29F8145D1078EC'
coinex = CoinEx(access_id, secret_key)
buyPrice = 0
sellPrice = 0
splittedCandle = gft(dataOfChart, delimiter=',')

def start():
    getDataForAnalyse()
    BB()

def getDataForAnalyse():
    csvFile = open("Data/DataForIndicator_BTC_BB.csv", 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={CryptoToTrade+'USDT'}&type={timeFrame}&limit=336")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

def BB():
    candlesClose = splittedCandle[:,2]
    currentCandleClose = candlesClose[-1]
    lastCandleClose = candlesClose[-2]
    global buyPrice
    buyPrice = currentCandleClose
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdevup=2, nbdevdn=2, matype=0)

    currentMiddleBB = middleBB[-1]

    if lastCandleClose < currentMiddleBB and currentCandleClose > currentMiddleBB:
        createOrder()
        wait(waitForSell)
        closeOrder()
    else:
        wait(waitForNextCheck)
   
def createOrder():
    # print(coinex.order_market(CryptoToTrade + 'USDT', 'buy', howMuchShouldIBuy))
    global orderCounter
    print('new order. #', orderCounter)
    orderCounter += 1
    # alarm('buy')

def closeOrder():
    # wallet = coinex.balance_info()
    # assest = (wallet[CryptoToTrade])['available']
    getDataForAnalyse()
    candleClose = splittedCandle[:,2][-1]
    global sellPrice
    sellPrice = candleClose
    profit = float(sellPrice / buyPrice)*100 - 100

    # print(coinex.order_limit(CryptoToTrade + 'USDT', 'sell', assest, sellPrice[-1]))
    print(f'Profit: {profit}')
    print('=======================================')

    return saveData(profit)

def saveData(tradeData):
    tradeDataCSV = open(saveDataHere, 'a', newline='')
    writer = csv.writer(tradeDataCSV)
    date = {time.ctime(time.time())}
    detailOfTrade = (str(tradeData)[:6]), (CryptoToTrade), (date)
    writer.writerow(detailOfTrade)
    tradeDataCSV.close()

def wait(second):
    while second:
        mins, secs = divmod(second, 60) 
        timer = 'Time Left: {:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        second -= 1

def alarm(type):
    if type == 'error':
        playsound('/Alarms/Error.mp3')
    elif type == 'buy':
        playsound('Alarms/Buy.mp3')
    elif type == 'profit':
        playsound('Alarms/Profit.mp3')
    elif type == 'sell':
        playsound('Alarms/Sell.mp3')
    else:
        playsound('Alarms/Error.mp3')

print('Turn on the openVPN')
while True:
    print(time.ctime(time.time()))
    start()