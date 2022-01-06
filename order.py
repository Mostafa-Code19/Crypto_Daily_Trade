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

    print(f'🕒 {app.cryptoToTrade} | Waiting For Enter-Price... | Current Price: {app.buyPrice} | {time.ctime(time.time())}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'🕒 {app.cryptoToTrade} | Waiting For Enter-Price... | Current Price: {app.buyPrice} | {time.ctime(time.time())}')
    
    while True:
        if indicator.BestPriceToBuy():
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

            print(f'#{app.orderCounter} | Open {app.cryptoToTrade} | {app.buyPrice} -> {str(app.buyPrice + (app.buyPrice * app.saveProfit) / 100)[:5]} | {app.boughtTime}')
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'#{app.orderCounter} | 🍏 {app.cryptoToTrade} | {app.buyPrice} -> {str(app.buyPrice + (app.buyPrice * app.saveProfit) / 100)[:5]} | {app.boughtTime}')

            waitForSellPosition(update, context)
        else:
            app.wait(app.fiveMinute)

def waitForSellPosition(update, context):
    while True:
        checkListForStopOrder(update, context)
        app.wait(app.fiveMinute)

def checkListForStopOrder(update, context):
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesHighest = splittedCandle[:,3]
    profit = checkProfit(candlesClose[-1])


    if profit >= app.saveProfit and indicator.BB_Sell(candlesClose, candlesHighest):
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
    global sellPrice, previousCrypto
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2][-1]
    sellPrice = candlesClose
    profit = checkProfit(sellPrice)
    previousCrypto = app.cryptoToTrade
    

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
    app.run(update, context)