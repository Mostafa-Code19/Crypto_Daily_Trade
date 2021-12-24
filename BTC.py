import requests, time, talib, csv
from playsound import playsound
from numpy import genfromtxt as gft
from coinex.coinex import CoinEx
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update
import os
from dotenv import load_dotenv

load_dotenv()

CryptoToTrade = 'BTC'
timeFrame = '15min'  #1min, 1hour, 1day, 1week
howMuchShouldIBuy = 30  # $
timePeriodForBB = 20
nbDev = .5
twoMinute = 2 * 60
fiveMinute = 5 * 60
saveProfit = .5
leastProfit = .25

telegram_token = os.getenv('TELEGRAM_KEY_BTC')
updater = Updater(telegram_token, use_context=True)
dispatcher = updater.dispatcher

access_id = os.getenv('COINEX_ACCESS_ID')
secret_key = os.getenv('COINEX_SECRET_KEY')
coinex = CoinEx(access_id, secret_key)
dataOfChart = 'Data/DataForIndicator_BTC.csv'
saveDataHere = 'Trade_Information/orderHistory_BTC.csv'
buyPrice = 0
sellPrice = 0
orderCounter = 0
totalProfits = 0
totalOrders = []

def listenToTelegram():
    start_handler = CommandHandler('start', start, run_async=True)
    dispatcher.add_handler(start_handler)

    totalOrders_handler = CommandHandler('total_orders', returnTotalOrders, run_async=True)
    dispatcher.add_handler(totalOrders_handler)

    totalProfit_handler = CommandHandler('total_profits', returnTotalProfits, run_async=True)
    dispatcher.add_handler(totalProfit_handler)

    updater.start_polling()

def returnTotalOrders(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Total Orders:{orderCounter} \n{totalOrders}')

def returnTotalProfits(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Total Profits:\n{str(totalProfits)[:4]}%')

def start(update: Update, context: CallbackContext):
    print(f'Analyze At: {time.ctime(time.time())}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Analyze At: {time.ctime(time.time())} | {CryptoToTrade}')

    while True:
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

    csvFile = open("Data/DataForIndicator_BTC.csv", 'w', newline='')
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

    print(candlesClose[-1])
    
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
    # print(coinex.order_market(CryptoToTrade + 'USDT', 'buy', howMuchShouldIBuy))
    # print('new order. #', orderCounter)
    orderCounter += 1

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'new order | #{orderCounter} | Time: {time.ctime(time.time())}')

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
    profit = checkProfit(candlesClose[-1])

    if candlesHighest[-1] > upperBB[-1] \
        and profit >= leastProfit \
        or profit >= saveProfit:
            closeOrder(update, context)

def checkProfit(sellPrice):
    profit = float(sellPrice / buyPrice)*100 - 100
    return profit

def closeOrder(update, context):
    # wallet = coinex.balance_info()
    # assest = (wallet[CryptoToTrade])['available']
    getDataForAnalyse()
    splittedCandle = gft(dataOfChart, delimiter=',')
    candleClose = splittedCandle[:,2][-1]
    global sellPrice
    sellPrice = candleClose
    profit = float(sellPrice / buyPrice)*100 - 100

    # print(coinex.order_limit(CryptoToTrade + 'USDT', 'sell', assest, sellPrice[-1]))
    # print(f'Profit: {str(profit)[:4]}')
    # print('=======================================')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'-------------------------------------------\nOrder {orderCounter} closed |\nprofit: {str(profit)[:4]}')

    saveData(profit)
    wait(fiveMinute)
    start(update, context)  # Start New Run

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

listenToTelegram()