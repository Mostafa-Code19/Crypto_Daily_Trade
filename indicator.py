import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    SMA_Ready = SMA(candlesClose)
    BBPerB_Ready = BBPerB(candlesVolume)
    MOM_Ready = MOM(candlesVolume)
    
    if OBV_Ready and SMA_Ready and BBPerB_Ready and MOM_Ready:
        return app.cryptoToTrade
    else:
        return None

def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def SMA(candlesClose):
    SMAs5 = talib.SMA(candlesClose, timeperiod=5)
    SMAs21 = talib.SMA(candlesClose, timeperiod=21)
            
    currentSMA5 = SMAs5[-1]
    currentSMA21 = SMAs21[-1]

    if currentSMA5 > currentSMA21:
        return True

def BBPerB(candlesClose):
    upper, middle, lower = talib.BBANDS(candlesClose, matype=0)
    above75Percent = middle[-1] + (upper[-1] - middle[-1]) / 2

    if candlesClose[-1] > above75Percent:
        return True

def MOM(candlesClose):
    MOMs = talib.MOM(candlesClose, timeperiod=5)
    currentMOM = MOMs[-1]

    if currentMOM > 0:
        return True