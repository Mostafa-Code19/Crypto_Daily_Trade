import requests, talib, csv, order, app
from numpy import genfromtxt as gft

dailyOrder = (15 * 995) / 60 / 24
whenStopLoss = -.25

buyPrice = 0
sellPrice = 0
candleIndex = 995
currentCheckedCandle = 3
candlesClose = None
candlesHighest = None
candlesLowest = None
candlesVolume = None
totalProfit = 0
orderCounter = 0
cryptoIndex = 0
resultAnalyze = {}

class DoneWithTheCoin(Exception): pass

def run(cryptosToCheck, update, context):
    global cryptoList
    cryptoList = cryptosToCheck

    for crypto in cryptoList:
        restartTheOrderResults()
        getDataForAnalyse()
        start()

    sortedCryptos = sorted(resultAnalyze.items(), key = lambda kv:(kv[1], kv[0]))
    app.cryptoToTrade = sortedCryptos[-1][0]

    order.createOrder(update, context)

def getDataForAnalyse():
    csvFile = open(app.dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={app.cryptoToTrade+'USDT'}&type={app.timeFrame}&limit={candleIndex + 5}")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

    global candlesClose, candlesHighest, candlesLowest, candlesVolume
    candlesClose = (gft(app.dataOfChart, delimiter=','))[:,2]
    candlesHighest = (gft(app.dataOfChart, delimiter=','))[:,3]
    candlesLowest = (gft(app.dataOfChart, delimiter=','))[:,4]
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
        currentCandleLowest = candlesLowest[int(currentCheckedCandle)]
        buyPrice = currentCandleLowest

        if OBV():
            createOrder()
        else:
            wait(app.fiveMinute)

        currentCheckedCandle += 1
        ifEndTheChartStop()

def OBV():
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[int(currentCheckedCandle) - 1] < OBVs[int(currentCheckedCandle)]:
        return True

def createOrder():
    ifEndTheChartStop()
    waitForSellPosition()

def closeOrder():
    global buyPrice, sellPrice, candlesClose, winTrade, lossTrade, zeroTrade, currentCheckedCandle, totalProfit, orderCounter
    sellPrice = candlesClose[int(currentCheckedCandle)]
    profit = (sellPrice / buyPrice)*100 - 100

    totalProfit += profit
    orderCounter += 1


    currentCheckedCandle += 1
    ifEndTheChartStop()
    wait(app.fiveMinute)
    start()

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
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    profit = checkProfit()

    if candlesHighest[int(currentCheckedCandle)] > middleBB[int(currentCheckedCandle)]  \
        and profit >= app.leastProfit \
        or profit >= app.saveProfit:
            closeOrder()

def checkProfit():
    sellPrice = candlesHighest[int(currentCheckedCandle)]
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def theEnd():
    resultAnalyze[app.cryptoToTrade] = float(str(totalProfit)[:4])
    raise DoneWithTheCoin