import requests, time, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx

CryptoToTrade = 'DOGE'
timeFrame = '15min'  #1min, 1hour, 1day, 1week
howMuchShouldIBuy = 30  # $
timePeriodForBB = 20
nbDev = .5

access_id = '9AB450BFC9574FF2A081D257A691D556'
secret_key = '1343602FFD3EA564E432286088A534EAEC29F8145D1078EC'
coinex = CoinEx(access_id, secret_key)
dataOfChart = 'Data/DataForIndicator_ALT.csv'
saveDataHere = 'Trade_Information/orderHistory_ALT.csv'
fiveMin = 5 * 60
saveProfit = 3.3
whenStopLoss = -1.5
buyPrice = 0
sellPrice = 0
orderCounter = 1

def start():
    print(time.ctime(time.time()))
    while True:
        try:
            getDataForAnalyse()
            checkListForMakingOrder()
        except Exception as e:
            print('Error...', e)
            print(time.ctime(time.time()))
            playsound('Alarms/Rocket.wav')
            continue
        
def getDataForAnalyse():
    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={CryptoToTrade+'USDT'}&type={timeFrame}&limit=150")
    response = (request.json())['data']

    csvFile = open("Data/DataForIndicator_ALT.csv", 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

def checkListForMakingOrder():
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]

    global buyPrice
    buyPrice = candlesClose[-2]

    MOM_Ready = MOM(candlesClose)
    BBPerB_Ready = BBPerB(candlesClose)
    SMA_Slow_Ready = SMA_Slow(candlesClose)
    SMA_Fast_Ready = SMA_Fast(candlesClose)
    
    print(f'MOM:{MOM_Ready} | BB:{BBPerB_Ready} | SMA-S:{SMA_Slow_Ready} | SMA-F:{SMA_Fast_Ready}')
    if MOM_Ready and BBPerB_Ready and SMA_Slow_Ready and SMA_Fast_Ready:
        createOrder()
    else:
        wait(fiveMin)

def SMA_Fast(candlesClose):
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
            
    currentSMA5 = SMAs5[-2]
    currentSMA21 = SMAs21[-2]

    if currentSMA5 > currentSMA21:
        return True
    else:
        return False

def SMA_Slow(candlesClose):
    SMAs50 = talib.SMA(candlesClose, timeperiod=50)
    SMAs200 = talib.SMA(candlesClose, timeperiod=200)
            
    currentSMA50 = SMAs50[-2]
    currentSMA200 = SMAs200[-2]

    if currentSMA50 > currentSMA200:
        return True
    else:
        return False

def BBPerB(candlesClose):
    upper, middle, lower = talib.BBANDS(candlesClose, matype=0)
    BBperB = middle[-2] + (upper[-2] - middle[-2]) / 2

    if candlesClose[-2] > BBperB:
        return True
    else:
        return False

def MOM(candlesClose):
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[-2]

    if currentMOM > 0:
        return True
    else:
        return False

def createOrder():
    global orderCounter
    # print(coinex.order_market(CryptoToTrade + 'USDT', 'buy', howMuchShouldIBuy))
    print('new order. #', orderCounter)
    print(time.ctime(time.time()))
    orderCounter += 1

    waitForSellPosition()

def wait(second):
    while second:
        mins, secs = divmod(second, 60) 
        timer = 'Time Left: {:02d}:{:02d}'.format(mins, secs) 
        second -= 1
        time.sleep(1) 
        print(timer, end="\r") 

def waitForSellPosition():
    while True:
        checkListForStopOrder()
        wait(fiveMin)

def checkListForStopOrder():
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesHighest = splittedCandle[:,3]
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdeDup=nbDev, nbdevdn=nbDev, matype=0)
    profit = checkProfit(candlesClose[-2])

    if candlesHighest[-2] > upperBB[-2] \
        or profit <= whenStopLoss \
        or profit >= saveProfit:
            closeOrder()

def checkProfit(sellPrice):
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def closeOrder():
    # wallet = coinex.balance_info()
    # assest = (wallet[CryptoToTrade])['available']
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candleClose = splittedCandle[:,2][-2]
    global sellPrice
    sellPrice = candleClose
    profit = float(sellPrice / buyPrice)*100 - 100

    # print(coinex.order_limit(CryptoToTrade + 'USDT', 'sell', assest, sellPrice[-2]))
    print(f'Profit: {profit}')
    print('=======================================')

    saveData(profit)
    start()  # Start New Run

def saveData(tradeData):
    tradeDataCSV = open(saveDataHere, 'a', newline='')
    writer = csv.writer(tradeDataCSV)
    date = {time.ctime(time.time())}
    detailOfTrade = (str(tradeData)[:6]), (CryptoToTrade), (date)
    writer.writerow(detailOfTrade)
    tradeDataCSV.close()

print('Turn on the openVPN')
start()