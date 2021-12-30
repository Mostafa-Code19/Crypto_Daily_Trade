import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    SMA_Ready = SMA(candlesClose)
    BB_Ready  = BB(candlesClose)
    MOM_Ready = MOM(candlesClose)
    Price_Ready = PriceGreen(candlesClose)
    
    if OBV_Ready and SMA_Ready and BB_Ready and MOM_Ready and Price_Ready():
        return app.cryptoToTrade
    else:
        return None

def PriceGreen(candlesClose):
    if candlesClose[-1] - candlesClose[-2] > 0:
        return True

def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def SMA(candlesClose):
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
    SMAs50 = talib.SMA(candlesClose, timeperiod=50)
    SMAs200 = talib.SMA(candlesClose, timeperiod=200)
            
    currentSMA5 = SMAs5[-1]
    currentSMA21 = SMAs21[-1]
    currentSMA50 = SMAs50[-1]
    currentSMA200 = SMAs200[-1]

    if currentSMA5 > currentSMA21 or currentSMA50 > currentSMA200:
        return True

def BB(candlesClose):
    upperBB, middleBB, lowerBB = talib.BBANDS(candlesClose, timeperiod=20, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if candlesClose[-1] <= upperBB[-1]:
        return True

def MOM(candlesClose):
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[-1]

    if currentMOM > 0:
        return True