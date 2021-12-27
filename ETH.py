import requests, time, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx
import os, time
from dotenv import load_dotenv
from prepetual_api.prepApi import CoinexPerpetualApi

load_dotenv()

CryptoToTrade = 'ETH'
timeFrame = '15min'  #1min, 1hour, 1day, 1week
howMuchShouldIBuy = 0.0065  # ETH
timePeriodForBB = 20
nbDev = .5
twoMinute = 2 * 60
fiveMinute = 5 * 60
saveProfit = .5
leastProfit = .25

access_id = os.getenv('COINEX_ACCESS_ID')
secret_key = os.getenv('COINEX_SECRET_KEY')
coinex = CoinEx(access_id, secret_key)
coinexPerpetual = CoinexPerpetualApi(access_id, secret_key)
dataOfChart = 'Data/DataForIndicator_ETH.csv'
saveDataHere = 'Trade_Information/orderHistory_ETH.csv'
buyPrice = 0
sellPrice = 0
orderCounter = 0
totalProfits = 0
totalOrders = []
startNew = True

def run(update, context):
    while startNew:
        try:
            getDataForAnalyse()
            checkListForMakingOrder(update, context)
        except Exception as e:
            print('Error...', e)
            print(time.ctime(time.time()))
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error!!!! # | time: {time.ctime(time.time())} | cause: {e}')
            playsound('Alarms/Rocket.wav')
            wait(fiveMinute)
            continue
        
def getDataForAnalyse():
    request = requests.get(f"https://api.coinex.com/v1/market/kline?market={CryptoToTrade+'USDT'}&type={timeFrame}&limit=150")
    response = (request.json())['data']

    csvFile = open("Data/DataForIndicator_ETH.csv", 'w', newline='')
    candleStickWriter = csv.writer(csvFile, delimiter = ',')
    #date, open, close, high, low, volume, amount | 5m-16h | 30m-336

    for candles in response:
        candleStickWriter.writerow(candles)
    csvFile.close()

def checkListForMakingOrder(update, context):
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesVolume = splittedCandle[:,5]

    MOM_Ready = MOM(candlesClose)
    BBPerB_Ready = BBPerB(candlesClose)
    SMA_Fast_Ready = SMA_Fast(candlesClose)
    OBV_Ready = OBV(candlesClose, candlesVolume)
    
    # print(f'MOM:{MOM_Ready} | BB:{BBPerB_Ready} | SMA-F:{SMA_Fast_Ready}')
    print(f'{MOM_Ready} | {BBPerB_Ready} | {SMA_Fast_Ready} | {OBV_Ready}')

    if MOM_Ready and BBPerB_Ready and SMA_Fast_Ready and OBV_Ready:
        global buyPrice
        buyPrice = candlesClose[-1]
        createOrder(update, context)
    else:
        wait(twoMinute)

def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)
    
    if OBVs[-2] < OBVs[-1]:
        return True
    else:
        return False

def SMA_Fast(candlesClose):
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
            
    currentSMA5 = SMAs5[-1]
    currentSMA21 = SMAs21[-1]

    if currentSMA5 > currentSMA21:
        return True
    else:
        return False

def BBPerB(candlesClose):
    upper, middle, lower = talib.BBANDS(candlesClose, matype=0)
    BBperB = middle[-1] + (upper[-1] - middle[-1]) / 2

    if candlesClose[-1] > BBperB:
        return True
    else:
        return False

def MOM(candlesClose):
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[-1]

    if currentMOM > 0:
        return True
    else:
        return False

def createOrder(update, context):
    global orderCounter
    # print('new order. #', orderCounter)

    # side 1 = sell, 2 = buy | effect_type 1 = always valid 2 = immediately or cancel 3 = fill or kill
    # option 1 = place maker orders only deafult 0

    print(
        coinexPerpetual.put_market_order(
            CryptoToTrade + 'USDT',
            2,  # side:buy
            howMuchShouldIBuy
        )
    )

    playsound('Alarms/Profit.mp3')

    orderCounter += 1

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'#{orderCounter} | new order')

    waitForSellPosition(update, context)

def wait(second):
    while second:
        mins, secs = divmod(second, 60) 
        timer = 'Time Left: {:02d}:{:02d}'.format(mins, secs) 
        second -= 1
        time.sleep(1) 
        print(timer, end="\r") 

def waitForSellPosition(update, context):
    while True:
        checkListForStopOrder(update, context)
        wait(twoMinute)

def checkListForStopOrder(update, context):
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesHighest = splittedCandle[:,3]
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=timePeriodForBB, nbdevup=nbDev, nbdevdn=nbDev, matype=0)
    profit = checkProfit(candlesHighest[-1])

    if candlesHighest[-1] > upperBB[-1] \
        and profit >= leastProfit \
        or profit >= saveProfit:
            closeOrder(update, context)

def checkProfit(sellPrice):
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def closeOrder(update, context):
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candleClose = splittedCandle[:,2][-1]
    global sellPrice
    sellPrice = candleClose
    profit = float(sellPrice / buyPrice)*100 - 100

    # account = coinexPerpetual.query_account()
    # assest_ETH = account['data']['ETH']['available']

    print(
        coinexPerpetual.close_market(
            CryptoToTrade + 'USDT',
            0  # Position Id
        )
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{orderCounter} closed |\nprofit: {str(profit)[:4]}')

    saveData(profit)

    playsound('Alarms/Profit.mp3')
    wait(99999999999999999999)
    # run(update, context)  # Start New Run

def saveData(tradeData):
    tradeDataCSV = open(saveDataHere, 'a', newline='')
    writer = csv.writer(tradeDataCSV)
    date = {time.ctime(time.time())}
    detailOfTrade = (str(tradeData)[:6]), (CryptoToTrade), (date)
    writer.writerow(detailOfTrade)
    tradeDataCSV.close()

    totalOrders.append([str(tradeData)[:6], CryptoToTrade, date])

    global totalProfits
    totalProfits += float(str(tradeData)[:6])