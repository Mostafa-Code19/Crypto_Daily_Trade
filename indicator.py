import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    BB_Ready  = BB(candlesClose)
    Price_Ready = PriceGreen(candlesClose)
    
    if OBV_Ready and BB_Ready and Price_Ready:
        return app.cryptoToTrade
    else:
        return None


def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def BB(candlesClose):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=20, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if candlesClose[-1] <= upperBB[-1]:
        return True

def PriceGreen(candlesClose):
    if candlesClose[-1] - candlesClose[-2] > 0:
        return True