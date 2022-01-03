import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesLowest = splittedCandle[:,4]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    SMA_Ready = SMA(candlesClose)
    BB_Ready = BB(candlesClose, candlesLowest)
    
    if OBV_Ready or SMA_Ready or BB_Ready:
        return app.cryptoToTrade
    else:
        return None


def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def SMA(candlesClose):
    SMAsFast = talib.SMA(candlesClose, timeperiod=8)
    SMAsSlow = talib.SMA(candlesClose, timeperiod=20)

    if SMAsFast[-1] >= SMAsSlow[-1]:
        return True

def BB(candlesClose, candlesLowest):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)
    lastLowerBB = lowerBB[-1]
    
    if candlesLowest[-1] <= lastLowerBB and candlesClose[-1] >= lastLowerBB:
        return True