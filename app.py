import time, csv, requests, indicator, historyAnalyzer
from playsound import playsound

from dotenv import load_dotenv
load_dotenv()

cryptoToTrade = None
fiveMinute = 5 * 60
timeFrame = '15min'  #1min, 1hour, 1day, 1week
dataOfChart = 'Data/DataForIndicator.csv'
ordersResults = 'Trade_Information\orderHistory.csv'
buyPrice = 0
sellPrice = 0
timePeriodForBB = 20
saveProfit = 2
nbDev = 1.5
leastProfit = 1
startNew = True
orderCounter = 0
cryptoList = ['ETH', 'BTC', 'DOGE', 'BNB', 'EOS', 'TRX', 'CRV', 'LTC', 'XRP', 'ADA', 'SHIB', 'DOT', 'XLM', 'BTT', 'ZEC', 'SOL', 'KSM', 'LUNA', 'AVAX', 'MATIC', 'CRO', 'ALGO', 'LINK', 'NEAR', 'BCH', 'OKB', 'ATOM', 'UNI', 'AXS', 'VET', 'SAND', 'THETA', 'EGLD', 'FIL', 'XTZ', 'XMR', 'ETC']
# cryptoList = ['ETH', 'BTC', 'DOGE', 'ADA']
currentProfitFromOrder = 0
cryptosReadyForTrade = []
totalOrders = []
totalProfits = 0

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
    print('Not Allowed Start New')
    while not startNew:
        wait(fiveMinute)
    run(update, context)

def run(update, context):
    while startNew:
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

                # except Exception as e:
                #     print('Error...', e)
                #     print(time.ctime(time.time()))

                #     try:
                #         context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error!!!! # | time: {time.ctime(time.time())} | cause: {e}')
                #     except:
                #         print('Connection to Telegram Lost!')

                #     playsound('Alarms/Rocket.wav')
                #     wait(fiveMinute)

                #     continue

        print('Coins Ready Indicator:')
        print(cryptosReadyForTrade)

        if cryptosReadyForTrade:
            print('Analyzing...')
            historyAnalyzer.run(cryptosReadyForTrade, update, context)
        else:
            print('No Coin Ready. Waiting...')
            wait(fiveMinute)
    
    waitForNextRun(update, context)