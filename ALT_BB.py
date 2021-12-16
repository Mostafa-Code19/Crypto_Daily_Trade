import requests, time, json, logging, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx

CryptoToTrade = 'DOGE'
timeFrame = '5min'  #1min, 1hour, 1day, 1week
howMuchShouldIBuy = 30  # $

access_id = '9AB450BFC9574FF2A081D257A691D556'
secret_key = '1343602FFD3EA564E432286088A534EAEC29F8145D1078EC'
coinex = CoinEx(access_id, secret_key)
dataOfChart = 'Data/DataForIndicator_ALT_BB.csv'
saveDataHere = 'Trade_Information/orderHistory_ALT_BB.csv'
fiveMin = 5 * 60
timePeriodForBB = 20
buyPrice = 0
sellPrice = 0
orderCounter = 1
nbDev = .5

def start():
    while True:
        try:
            print(time.ctime(time.time()))
            getDataForAnalyse()
            BB()
        except:
            return
        
def getDataForAnalyse():
    csvFile = open("Data/DataForIndicator_ALT_BB.csv", 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={CryptoToTrade+'USDT'}&type={timeFrame}&limit=30")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

def BB():
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    global buyPrice
    buyPrice = candlesClose[-1]
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdevup=nbDev, nbdevdn=nbDev, matype=0)

    if candlesClose[-1] < lowerBB[-1] and RSI() == 'RSI_OK':
        createOrder()
    else:
        wait(fiveMin)

def createOrder():
    # print(coinex.order_market(CryptoToTrade + 'USDT', 'buy', howMuchShouldIBuy))
    global orderCounter
    print('new order. #', orderCounter)
    orderCounter += 1

    waitForSellPosition()

def RSI():
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    RSIs = talib.RSI(candlesClose, timeperiod=14)
    currentRSI = RSIs[-1]

    if currentRSI >= 40:
        return 'RSI_OK'

def closeOrder(type):
    # wallet = coinex.balance_info()
    # assest = (wallet[CryptoToTrade])['available']
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candleClose = splittedCandle[:,2][-1]
    global sellPrice
    sellPrice = candleClose
    profit = float(sellPrice / buyPrice)*100 - 100

    # print(coinex.order_limit(CryptoToTrade + 'USDT', 'sell', assest, sellPrice[-1]))
    print(f'Profit: {profit}')
    print('=======================================')

    saveData(profit)

    if type == 'loss' and checkTheTrend() != 'upTrend':
        wait(120*60)

    start()  # Start New Run

def checkTheTrend():
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    if candlesClose[-1] > (candlesClose[-1 - 144]):
        return 'upTrend'

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

def waitForSellPosition():
    while True:
        checkPosition()
        wait(fiveMin)

def checkPosition():
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]

    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdevup=nbDev, nbdevdn=nbDev, matype=0)

    print(candlesClose[-1])
    print(upperBB[-1])

    profit = checkProfit(candlesClose[-1])

    if candlesClose[-1] > upperBB[-1] or profit <= -1:
        print('going to sell')

        if profit <= -1:
            closeOrder('loss')
        else:
            closeOrder('win')

def checkProfit(sellPrice):
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

print('Turn on the openVPN')
start()