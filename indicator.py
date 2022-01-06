import talib, app
from order import checkProfit
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesHighest = splittedCandle[:,3]
    candlesLowest = splittedCandle[:,4]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    EMA_Ready = EMA(candlesClose)
    BB_Ready = BB(candlesClose, candlesLowest)
    MFI_Ready = MFI(candlesHighest, candlesLowest, candlesClose, candlesVolume)
    
    if OBV_Ready or EMA_Ready or BB_Ready or MFI_Ready:
        return app.cryptoToTrade
    else:
        return None


def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def EMA(candlesClose):
    EMAsFast = talib.EMA(candlesClose, timeperiod=9)
    EMAsSlow = talib.EMA(candlesClose, timeperiod=20)

    if EMAsFast[-1] >= EMAsSlow[-1]:
        return True

def BB(candlesClose, candlesLowest):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)
    lastLowerBB = lowerBB[-1]

    if candlesLowest[-1] <= lastLowerBB and candlesClose[-1] >= lastLowerBB:
        return True

def BB_Bottom(candlesClose, candlesLowest):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if candlesLowest[-1] <= lowerBB[-1]:
        return True

def MFI(high, low, close, volume):
    MFIs = talib.MFI(high, low, close, volume, timeperiod=14)

    if MFIs[-1] <= 20:
        return True

def BB_Sell(close, high):
    upperBB, middleBB, lowerBB = talib.BBANDS(close, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if high[-1] >= upperBB[-1]:
        return True

def BestPriceToBuy():
    app.getDataForAnalyse()
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesLowest = splittedCandle[:,4]

    profit = checkProfit(candlesClose[-1])
    if BB_Bottom(candlesClose, candlesLowest) \
        or profit <= -2 \
        or profit >= 1:
            return True
