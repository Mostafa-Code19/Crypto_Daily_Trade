import time, csv, requests, indicator, historyAnalyzer, math
from playsound import playsound
from dotenv import load_dotenv

load_dotenv()

cryptoList = ['ETH', 'BTC', 'DOGE', 'BNB', 'EOS', 'TRX', 'CRV', 'LTC', 'XRP', 'ADA', 'SHIB', 'DOT', 'XLM', 'BTT', 'ZEC', 'SOL', 'KSM', 'LUNA', 'AVAX', 'MATIC', 'CRO', 'ALGO', 'LINK', 'NEAR', 'BCH', 'OKB', 'ATOM', 'UNI', 'AXS', 'VET', 'SAND', 'THETA', 'EGLD', 'FIL', 'XTZ', 'XMR', 'ETC']
timeFrame = '15min'  #1min, 1hour, 1day, 1week
timeFrameInInteger = 15
# saveProfit = 1.5
leastProfit = 1.5
thirtySecond = 30
nbDev = 1.4
timePeriodForBB = 20
# requiredProfitFromPrevious = 1.5
buyPrice = 0
sellPrice = 0
cryptoToTrade = None
dataOfChart = 'Data/DataForIndicator.csv'
ordersResults = 'Trade_Information/orderHistory.csv'
startNew = True
orderCounter = 0
currentProfitFromOrder = 0
cryptosReadyForTrade = []
totalOrders = []
totalProfits = 0
boughtTime = None
waitForNewCandle = 0

def wait(second):
    while second:
        mins, secs = divmod(second, 60) 
        timer = 'Time Left: {:02d}:{:02d}'.format(mins, secs) 
        second -= 1
        time.sleep(1) 
        print(timer, end="\r") 
        
def getDataForAnalyse():
    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={cryptoToTrade+'USDT'}&type={timeFrame}&limit=150")
    response = (request.json())['data']

    csvFile = open(dataOfChart, 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

class EndCoin(Exception): pass

def waitForNextRun(update, context):
    print('Not Allowed Start New...')
    while not startNew:
        wait(thirtySecond)
    run(update, context)

def restartInformationForNewTrade():
    global buyPrice, sellPrice, cryptoToTrade, currentProfitFromOrder, cryptosReadyForTrade, boughtTime

    boughtTime = None
    cryptoToTrade = None
    buyPrice = 0
    sellPrice = 0
    currentProfitFromOrder = 0
    cryptosReadyForTrade = []

def pre_Run(update, context):
    print('Waiting for New Candle...')

    while not newCandleBegin():
        wait(waitForNewCandle * 60)

    run(update, context)

def run(update, context):
    while startNew:
        indicate(update, context)
        analyzeHistory(update, context)
    
    waitForNextRun(update, context)

def newCandleBegin():
    global waitForNewCandle

    currentMinute = time.localtime().tm_min
    howLongIsTheNewCandle = currentMinute % timeFrameInInteger

    if howLongIsTheNewCandle <= 1:
        return True
    else:
        waitForNewCandle = timeFrameInInteger - howLongIsTheNewCandle
        return False

def indicate(update, context):
    print('Checking Cryptos indicator...')
    for crypto in cryptoList:
        print(f' {crypto}  ', end='\r')
        
        while True:
            try:
                global cryptoToTrade
                cryptoToTrade = crypto
                getDataForAnalyse()
                indicatorResult = indicator.checkListForMakingOrder(update, context)
                if indicatorResult:
                    cryptosReadyForTrade.append(indicatorResult)
                raise EndCoin

            except EndCoin:
                break

    print('Coins Ready Indicator:')
    print(cryptosReadyForTrade)

def analyzeHistory(update, context):
    if cryptosReadyForTrade:
        try:
            print('Analyzing...')
            historyAnalyzer.run(cryptosReadyForTrade, update, context)
        except historyAnalyzer.notEnoughPreviousProfit:
            wait(30 * 60)
    else:
        print('No Coin Ready. Waiting...')
        wait(30 * 60)  # 30 min