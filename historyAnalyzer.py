import requests, talib, csv, order, app
from numpy import genfromtxt as gft

dailyOrder = (15 * 995) / 60 / 24
buyPrice = 0
sellPrice = 0
candleIndex = 995
currentCheckedCandle = 3
candlesClose = None
candlesVolume = None
totalProfit = 0
orderCounter = 0
cryptoIndex = 0
resultAnalyze = {}
cryptoToCheck = None

class DoneWithTheCoin(Exception): pass

def run(cryptosToCheck, update, context):
    for crypto in cryptosToCheck:
        global cryptoToCheck
        cryptoToCheck = crypto
        restartTheOrderResults()
        getDataForAnalyse()
        start()

    sortedCryptos = sorted(resultAnalyze.items(), key = lambda kv:(kv[1], kv[0]))
    print(resultAnalyze)
    app.cryptoToTrade = sortedCryptos[-1][0]

    order.createOrder(update, context)

def getDataForAnalyse():
    csvFile = open(app.dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={cryptoToCheck+'USDT'}&type={app.timeFrame}&limit={candleIndex + 5}")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

    global candlesClose, candlesVolume
    candlesClose = (gft(app.dataOfChart, delimiter=','))[:,2]
    candlesVolume = (gft(app.dataOfChart, delimiter=','))[:,5]

def start():
    while currentCheckedCandle < candleIndex:
        try:        
            checkListForMakingOrder()
        except DoneWithTheCoin:
            break
        
def checkListForMakingOrder():
    global currentCheckedCandle, buyPrice

    while currentCheckedCandle != candleIndex:
        buyPrice = candlesClose[int(currentCheckedCandle)]

        if MOM() and BB() and SMA() and OBV() and PriceGreen():
            createOrder()
        else:
            wait(app.fiveMinute)

        currentCheckedCandle += 1
        ifEndTheChartStop()

def PriceGreen(candlesClose):
    if candlesClose[int(currentCheckedCandle)] - candlesClose[int(currentCheckedCandle) - 1] > 0:
        return True

def OBV():
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[int(currentCheckedCandle) - 1] < OBVs[int(currentCheckedCandle)]:
        return True

def SMA():
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
    SMAs50 = talib.SMA(candlesClose, timeperiod=50)
    SMAs200 = talib.SMA(candlesClose, timeperiod=200)
            
    currentSMA5 = SMAs5[int(currentCheckedCandle)]
    currentSMA21 = SMAs21[int(currentCheckedCandle)]
    currentSMA50 = SMAs50[int(currentCheckedCandle)]
    currentSMA200 = SMAs200[int(currentCheckedCandle)]

    if currentSMA5 > currentSMA21 or currentSMA50 > currentSMA200:
        return True

def BB(candlesClose):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=20, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if candlesClose[int(currentCheckedCandle)] <= upperBB[int(currentCheckedCandle)]:
        return True

def MOM():
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[int(currentCheckedCandle)]

    if currentMOM > 0:
        return True

def createOrder():
    ifEndTheChartStop()
    waitForSellPosition()

def restartTheOrderResults():
    global currentCheckedCandle, orderCounter, totalProfit, buyPrice, sellPrice
    currentCheckedCandle = 3
    buyPrice = 0
    sellPrice = 0
    orderCounter = 0
    totalProfit = 0

def wait(second):
    global currentCheckedCandle
    for i in range(int(second / 60 / 5)):
        currentCheckedCandle += 1
        ifEndTheChartStop()

def waitForSellPosition():
    while True:
        checkPosition()
        wait(app.fiveMinute)

def ifEndTheChartStop():
    if (currentCheckedCandle > candleIndex):
        theEnd()

def checkPosition():
    profit = checkProfit()

    if profit >= app.saveProfit:
        closeOrder()

def closeOrder():
    global sellPrice, currentCheckedCandle, totalProfit, orderCounter
    sellPrice = candlesClose[int(currentCheckedCandle)]
    profit = (sellPrice / buyPrice)*100 - 100
    totalProfit += profit
    orderCounter += 1
    currentCheckedCandle += 1
    ifEndTheChartStop()
    wait(app.fiveMinute)
    start()

def checkProfit():
    sellPrice = candlesClose[int(currentCheckedCandle)]
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def theEnd():
    resultAnalyze[cryptoToCheck] = float(str(totalProfit)[:4])
    raise DoneWithTheCoin