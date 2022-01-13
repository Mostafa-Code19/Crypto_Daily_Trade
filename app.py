import time, csv, requests, indicator, historyAnalyzer, math
from playsound import playsound
from dotenv import load_dotenv

load_dotenv()

cryptoList = [
    'ATOM', 'SAND', 'ETH', 'SOL', 'DOT', 'SHIB', 'LTC', 'BTC', 'DOGE', 'BNB', 'EOS', 'TRX', 'CRV', 'ETC', \
    'XRP', 'XLM', 'GRT', 'REN', 'CEL', \
    'ZEC',  'MATIC', 'JST', \
    'CRO', 'NEAR', 'BCH', 'OKB', \
    'ATOM', 'UNI', 'AXS', 'VET',  'THETA', \
    'EGLD', 'FIL', 'XTZ', 'XMR', 'LINK', 'ADA',
]

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
        wait(5 * 60)
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

    while not newCandleBegin():
        print('Waiting for New Candle...')
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

    
    if len(cryptosReadyForTrade) != 0:
        print('Coins Ready Indicator:')
        print(cryptosReadyForTrade)

def analyzeHistory(update, context):
    if cryptosReadyForTrade:
        print('History analyzing...')
        historyAnalyzer.run(cryptosReadyForTrade, update, context)
    else:
        print('There is no coin to trade. next scan in 5min...')
        wait(5 * 60)  # 10 min