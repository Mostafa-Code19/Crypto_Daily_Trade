import requests, time, json, logging, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx
import sys

cryptoList = ['ETH', 'BTC', 'DOGE', 'BNB', 'EOS', 'TRX', 'CRV', 'LTC', 'XRP', 'ADA', 'SHIB', 'DOT', 'XLM', 'BTT', 'ZEC', 'SOL', 'KSM']

# CryptoToTrade = 'ETH'
# CryptoToTrade = 'BTC'
# CryptoToTrade = 'DOGE'
# CryptoToTrade = 'BNB'
# CryptoToTrade = 'CRV'
# CryptoToTrade = 'EOS'
# CryptoToTrade = 'TRX'
# CryptoToTrade = 'LTC'
# CryptoToTrade = 'XRP'
# CryptoToTrade = 'ADA'
# CryptoToTrade = 'CHZ'
# CryptoToTrade = 'XLM'
# CryptoToTrade = 'BTT'
# CryptoToTrade = 'ZEC'
# CryptoToTrade = 'DOT'
# CryptoToTrade = 'SHIB'
# CryptoToTrade = 'SOL'
# CryptoToTrade = 'KSM'

timeFrame = '1hour'  #1min, 1hour, 1day, 1week
fiveMinute = 5 * 60  # 5 minute
dataOfChart = './Data/historyAnalyzer.csv'
ordersResults = './Trade_Information/historyAnalyzer.csv'
timePeriodForBB = 20
nbdev = 1
saveProfit = 2
leastProfit = 1

orderCounter = 1
access_id = '9AB450BFC9574FF2A081D257A691D556'
secret_key = '1343602FFD3EA564E432286088A534EAEC29F8145D1078EC'
coinex = CoinEx(access_id, secret_key)
buyPrice = 0
sellPrice = 0
candleIndex = 995  # 3.4 day before
currentCheckedCandle = 3
candlesClose = None
candlesHighest = None
candlesLowest = None
candlesVolume = None

def start():
    while int(currentCheckedCandle) < candleIndex:
        try:
            checkListForMakingOrder()
        except Exception as e:
            print("Error: ", e)
            wait(fiveMinute)
            break

def getDataForAnalyse():
    csvFile = open(dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={CryptoToTrade+'USDT'}&type={timeFrame}&limit={candleIndex + 5}")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

    global candlesClose
    candlesClose = (gft(dataOfChart, delimiter=','))[:,2]

    global candlesHighest
    candlesHighest = (gft(dataOfChart, delimiter=','))[:,3]

    global candlesLowest
    candlesLowest = (gft(dataOfChart, delimiter=','))[:,4]

    global candlesVolume
    candlesVolume = (gft(dataOfChart, delimiter=','))[:,5]

def checkListForMakingOrder():
    global currentCheckedCandle
    global buyPrice

    while int(currentCheckedCandle) != candleIndex:
        currentCandleLowest = candlesLowest[int(currentCheckedCandle)]
        buyPrice = currentCandleLowest

        if MOM() and BBPerB() and SMA() and OBV():
            createOrder()
        else:
            wait(fiveMinute)


        c = int(currentCheckedCandle)
        currentCheckedCandle = c + 1

def SMA():
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
            
    currentSMA5 = SMAs5[int(currentCheckedCandle)]
    currentSMA21 = SMAs21[int(currentCheckedCandle)]

    if currentSMA5 > currentSMA21:
        return True

def BBPerB():
    upper, middle, lower = talib.BBANDS(candlesClose, matype=0)
    BBperB = middle[int(currentCheckedCandle)] + (upper[int(currentCheckedCandle)] - middle[int(currentCheckedCandle)]) / 2

    if candlesClose[int(currentCheckedCandle)] > BBperB:
        return True

def OBV():
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[int(currentCheckedCandle) - 1] < OBVs[int(currentCheckedCandle)]:
        return True

def MOM():
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[int(currentCheckedCandle)]

    if currentMOM > 0:
        return True

def createOrder():
    global orderCounter
    # print('new order. #', orderCounter)
    orderCounter += 1
    
    waitForSellPosition()

def closeOrder():
    global candlesClose
    global currentCheckedCandle
    global sellPrice
    sellPrice = candlesClose[int(currentCheckedCandle)]
    profit = float(sellPrice / buyPrice)*100 - 100

    saveData(profit)

    c = int(currentCheckedCandle)
    currentCheckedCandle = c + 1
    
    wait(fiveMinute)
    start()

def saveData(profit):
    tradeDataCSV = open(ordersResults, 'a', newline='')
    writer = csv.writer(tradeDataCSV)
    detailOfTrade = (str(profit)[:6]), (int(currentCheckedCandle))
    writer.writerow(detailOfTrade)
    tradeDataCSV.close()

def restartTheOrderResults():
    tradeDataCSV = open(ordersResults, 'w', newline='')
    tradeDataCSV.close()

def wait(second):
    global currentCheckedCandle

    c = int(currentCheckedCandle)
    currentCheckedCandle = c + second / 60 / 5

def waitForSellPosition():
    while True:
        checkPosition()
        wait(fiveMinute)

def checkPosition():
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdevup=nbdev, nbdevdn=nbdev, matype=0)

    profit = checkProfit()

    if candlesHighest[int(currentCheckedCandle)] > upperBB[int(currentCheckedCandle)]  \
        and profit >= leastProfit \
        or profit >= saveProfit:
            closeOrder()

def checkProfit():
    sellPrice = candlesHighest[int(currentCheckedCandle)]
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

print('Turn on the openVPN')
print(time.ctime(time.time()))

getDataForAnalyse()
restartTheOrderResults()
start()