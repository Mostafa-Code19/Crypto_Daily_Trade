import requests, talib, csv, order, app, indicator
from numpy import genfromtxt as gft

buyPrice = 0
sellPrice = 0
candleIndex = 995  # from 24 hour history
dailyOrder = (15 * candleIndex) / 60 / 24
currentCheckedCandle = 20
candlesClose = None
candlesVolume = None
candlesHighest = None
candlesLowest = None
totalProfit = 0
orderCounter = 0
cryptoIndex = 0
resultAnalyze = {}
cryptoToCheck = None
expireBestPriceToEnterIn = 7  # 1 = 15Min

class DoneWithTheCoin(Exception): pass
# class notEnoughPreviousProfit(Exception): pass

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

    # if bestCryptoToTradeByHistory[1] >= app.requiredProfitFromPrevious:
    app.cryptoToTrade = bestCryptoToTradeByHistory[0]
    order.createOrder(update, context)

    # else:
    #     raise notEnoughPreviousProfit

def getDataForAnalyse():
    csvFile = open(app.dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={cryptoToCheck+'USDT'}&type={app.timeFrame}&limit={candleIndex + 5}")
    response = (request.json())['data']

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

    global candlesClose, candlesVolume, candlesLowest, candlesHighest
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
    global currentCheckedCandle, buyPrice, expireWaitingForBestPrice

    while currentCheckedCandle != candleIndex:
        buyPrice = candlesClose[currentCheckedCandle]

        if (EMA_Above_BB() or EMA() or OBV() \
            or BB_LowestBelowLowerCloseAboveLower() or MFI() \
            or MOM() or MACD() or MACD_Divergence_Uptrend() \
            ) and SMA_TodayCloseAboveBeforeClose() and SMA_RSI() and RSI():
            
                createOrder()
        else:
            wait(app.thirtySecond)

        currentCheckedCandle += 1
        ifEndTheChartStop()

# def GREEN():
#     if candlesClose[currentCheckedCandle] > candlesClose[currentCheckedCandle - 1]:
#         return True

def BB_LowestBelowLowerCloseAboveLower():
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=2, nbdevdn=2, matype=0)

    if candlesLowest[currentCheckedCandle] <= lowerBB[currentCheckedCandle] and candlesClose[currentCheckedCandle] >= lowerBB[currentCheckedCandle]:
        return True

def EMA():
    EMAsFast = talib.EMA(candlesClose, timeperiod=9)
    EMAsSlow = talib.EMA(candlesClose, timeperiod=20)

    if EMAsFast[currentCheckedCandle] >= EMAsSlow[currentCheckedCandle]:
        return True

def SMA_TodayCloseAboveBeforeClose():
    the72 = (72 * 60) / 15
    lowestOf72 = talib.EMA(candlesClose, timeperiod=the72)

    if lowestOf72[currentCheckedCandle] < candlesClose[currentCheckedCandle]:
        return True

def RSI_Overbought():
    RSIs = talib.RSI(candlesClose, timeperiod=14)
    
    if 70 <= RSIs[currentCheckedCandle]:
        return True
    
def SMA_RSI():
    RSIs = talib.RSI(candlesClose, timeperiod=14)
    SMAs = talib.SMA(RSIs, timeperiod=14)

    if 70 > RSIs[currentCheckedCandle] > SMAs[currentCheckedCandle]:
        return True

def EMA_Above_BB():
    EMAs = talib.EMA(candlesClose, timeperiod=20)
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if EMAs[currentCheckedCandle] >= middleBB[currentCheckedCandle]:
        return True

def MACD():
    macd, signal, macdhist = talib.MACD(candlesClose, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[currentCheckedCandle - 1] < macd[currentCheckedCandle]:
        return True 
 
def MOM():
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[currentCheckedCandle]

    if currentMOM > 0:
        return True
    
def MFI():
    MFIs = talib.MFI(candlesHighest, candlesLowest, candlesClose, candlesVolume, timeperiod=14)

    if MFIs[currentCheckedCandle] <= 20:
        return True
    
def OBV():
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[currentCheckedCandle - 1] < OBVs[currentCheckedCandle]:
        return True

def RSI():
    RSIs = talib.RSI(candlesClose, timeperiod=14)
    
    if 70 > RSIs[currentCheckedCandle] > RSIs[currentCheckedCandle - 1]:
        return True

def RSI_Above50():
    RSIs = talib.RSI(candlesClose, timeperiod=14)
    
    if 50 <= RSIs[currentCheckedCandle]:
        return True

def MACD_Divergence_Uptrend():
    macd, signal, macdhist = talib.MACD(candlesClose, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[currentCheckedCandle - 4] < macd[currentCheckedCandle]:
        return True 

def MACD_Divergence_Downtrend():
    macd, signal, macdhist = talib.MACD(candlesClose, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[currentCheckedCandle - 4] > macd[currentCheckedCandle]:
        return True 

def createOrder():
    global buyPrice
    buyPrice = candlesClose[currentCheckedCandle]
    
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
    if second >= 300:
        for i in range(int(second / 60 / 5)):
            currentCheckedCandle += 1
            ifEndTheChartStop()
    else:
        for i in range(second):
            currentCheckedCandle += 1
            ifEndTheChartStop()

def waitForSellPosition():
    while True:
        checkPosition()
        wait(app.thirtySecond)

def ifEndTheChartStop():
    if (currentCheckedCandle > candleIndex):
        theEnd()

def checkPosition():
    profit = checkProfit()

    if profit >= app.leastProfit and (MACD_Divergence_Downtrend() or RSI_Overbought()):
        closeOrder()

def closeOrder():
    global sellPrice, currentCheckedCandle, totalProfit, orderCounter
    sellPrice = candlesClose[currentCheckedCandle]
    profit = (sellPrice / buyPrice)*100 - 100
    totalProfit += profit
    orderCounter += 1
    currentCheckedCandle += 1
    ifEndTheChartStop()
    wait(app.thirtySecond)
    start()

def checkProfit():
    sellPrice = candlesClose[currentCheckedCandle]
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def theEnd():
    # resultAnalyze[cryptoToCheck] = float(str(totalProfit)[:6])
    
    if orderCounter:
        resultAnalyze[cryptoToCheck] = float(str(totalProfit / orderCounter)[:4])
    else:
        resultAnalyze[cryptoToCheck] = 0
          
    raise DoneWithTheCoin