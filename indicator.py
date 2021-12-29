import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)

    if OBV_Ready:
        return app.cryptoToTrade
    else:
        return None

def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True
    else:
        return False