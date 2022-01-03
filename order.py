import app, talib, csv, time, indicator
from numpy import genfromtxt as gft
from prepetual_api.prepApi import CoinexPerpetualApi

candlesClose = None
def createOrder(update, context):
    
    print('Ordering: ', app.cryptoToTrade)

    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    app.buyPrice = candlesClose[-1]

    app.boughtTime = time.ctime(time.time())

    # side 1 = sell, 2 = buy | effect_type 1 = always valid 2 = immediately or cancel 3 = fill or kill
    # option 1 = place maker orders only deafult 0

    # print(
    #     coinexPerpetual.put_market_order(
    #         app.cryptoToTrade + 'USDT',
    #         2,  # side:buy
    #         howMuchShouldIBuy // buyPrice  # convert to amount of crypto to buy
    #     )
    # )

    # playsound('Alarms/Profit.mp3')

    app.orderCounter += 1

    print(f'#{app.orderCounter} | new order | {app.cryptoToTrade} | {app.buyPrice} | {app.boughtTime}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'#{app.orderCounter} | new order | {app.cryptoToTrade} | {app.buyPrice} | {app.boughtTime}')

    waitForSellPosition(update, context)

def waitForSellPosition(update, context):
    while True:
        checkListForStopOrder(update, context)
        app.wait(app.fiveMinute)

def checkListForStopOrder(update, context):
    app.getDataForAnalyse()

    profit = checkProfit(candlesClose[-1])


    if profit >= app.saveProfit:
        closeOrder(update, context)

def checkProfit(sellPrice):
    profit = float(sellPrice / app.buyPrice)*100 - 100
    app.currentProfitFromOrder = profit
    return profit

def saveData(tradeData):
    tradeDataCSV = open(app.ordersResults, 'a', newline='')
    writer = csv.writer(tradeDataCSV)
    date = {time.ctime(time.time())}
    detailOfTrade = (str(tradeData)[:6]), (app.cryptoToTrade), (date)
    writer.writerow(detailOfTrade)
    tradeDataCSV.close()

    app.totalOrders.append([str(tradeData)[:6], app.cryptoToTrade, date])
    app.totalProfits += float(str(tradeData)[:6])

def closeOrder(update, context):
    global sellPrice
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    sellPrice = candlesClose[-1]
    profit = checkProfit(sellPrice)
    

    # print(
    #     coinexPerpetual.close_market(
    #         app.cryptoToTrade + 'USDT',
    #         0  # Position Id
    #     )
    # )

    print(f'{app.orderCounter} closed |\n {app.cryptoToTrade} |\nprofit: {str(profit)[:4]}')

    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'{app.orderCounter} closed |\n {app.cryptoToTrade} |\nprofit: {str(profit)[:4]}')
    except:
        print('Connection to Telegram Lost!')

    saveData(profit)

    app.currentProfitFromOrder = 0
    app.buyPrice = 0

    app.restartInformationForNewTrade()
    app.run(update, context)