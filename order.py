import app, talib, csv, time, indicator
from numpy import genfromtxt as gft
from prepetual_api.prepApi import CoinexPerpetualApi

def setBuyPrice():
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    app.buyPrice = candlesClose[-1]

def createOrder(update, context):
    setBuyPrice()
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

    print(f'#{app.orderCounter} | Open {app.cryptoToTrade} | {app.buyPrice} -> {str(app.leastProfit / 100)[:5]} | {app.boughtTime}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'#{app.orderCounter} | 🍏 {app.cryptoToTrade} | {app.buyPrice} -> {str(app.buyPrice + app.leastProfit / 100)[:5]} | {app.boughtTime}')

    waitForSellPosition(update, context)

def waitForSellPosition(update, context):
    while True:
        checkListForStopOrder(update, context)
        app.wait(app.thirtySecond)

def checkListForStopOrder(update, context):
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    
    profit = app.checkProfit()

    if profit >= app.leastProfit and indicator.MACD_Divergence_Downtrend(candlesClose):
        closeOrder(update, context)

def checkProfit():
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    sellPrice = candlesClose[-1]
    
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
    profit = checkProfit()

    # print(
    #     coinexPerpetual.close_market(
    #         app.cryptoToTrade + 'USDT',
    #         0  # Position Id
    #     )
    # )

    print(f'#{app.orderCounter} | Close {app.cryptoToTrade} | profit: {str(profit)[:4]} | {time.ctime(time.time())}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'#{app.orderCounter} | 🍎 {app.cryptoToTrade} | profit: {str(profit)[:4]} | {time.ctime(time.time())}')

    saveData(profit)

    app.currentProfitFromOrder = 0
    app.buyPrice = 0

    app.restartInformationForNewTrade()
    app.wait(app.thirtySecond)
    app.run(update, context)