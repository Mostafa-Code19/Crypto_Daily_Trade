import requests, talib, csv, order, app, indicator
from numpy import genfromtxt as gft

buyPrice = 0
sellPrice = 0
candleIndex = 200  # from 24 hour history
dailyOrder = (15 * candleIndex) / 60 / 24
currentCheckedCandle = 100
candlesClose = None
candlesVolume = None
candlesLowest = None
totalProfit = 0
orderCounter = 0
cryptoIndex = 0
requiredProfitFromPrevious = 1.5
resultAnalyze = {}
cryptoToCheck = None

class DoneWithTheCoin(Exception): pass

def run(cryptosToCheck, update, context):
    for crypto in cryptosToCheck:
        print(f' {crypto} ', end='\r')
        global cryptoToCheck
        cryptoToCheck = crypto
        restartTheOrderResults()
        getDataForAnalyse()
        start()

    print(resultAnalyze)

    sortedCryptos = sorted(resultAnalyze.items(), key = lambda kv:(kv[1], kv[0]))
    bestCryptoToTradeByHistory = sortedCryptos[-1]

    if bestCryptoToTradeByHistory[1] >= requiredProfitFromPrevious:
        app.cryptoToTrade = bestCryptoToTradeByHistory[0]
        order.createOrder(update, context)
    else:
        app.run(update, context)

def getDataForAnalyse():
    csvFile = open(app.dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={cryptoToCheck+'USDT'}&type={app.timeFrame}&limit={candleIndex + 5}", proxies=app.proxies)
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

    global candlesClose, candlesVolume, candlesLowest
    candlesClose = (gft(app.dataOfChart, delimiter=','))[:,2]
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
        buyPrice = candlesClose[int(currentCheckedCandle)]

        if SMA() or BB() or OBV():
            createOrder()
        else:
            wait(app.fiveMinute)

        currentCheckedCandle += 1
        ifEndTheChartStop()

def OBV():
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[int(currentCheckedCandle) - 1] < OBVs[int(currentCheckedCandle)]:
        return True

def SMA():
    SMAsFast = talib.SMA(candlesClose, timeperiod=8)
    SMAsSlow = talib.SMA(candlesClose, timeperiod=20)

    if SMAsFast[int(currentCheckedCandle)] >= SMAsSlow[int(currentCheckedCandle)]:
        return True

def BB():
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if candlesLowest[int(currentCheckedCandle)] <= lowerBB[int(currentCheckedCandle)]:
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