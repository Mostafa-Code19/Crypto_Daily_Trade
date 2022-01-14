import talib, app
from numpy import genfromtxt as gft

def checkListForMakingOrder(update, context):
    print(app.cryptoToTrade, end='\r')
    splittedCandle = gft(app.dataOfChart, delimiter=',')
    candlesClose = splittedCandle[:,2]
    candlesHighest = splittedCandle[:,3]
    candlesLowest = splittedCandle[:,4]
    candlesVolume = splittedCandle[:,5]

    OBV_Ready = OBV(candlesClose, candlesVolume)
    RSI_Ready = RSI(candlesClose)
    MACD_Uptrend = MACD_Divergence_Uptrend(candlesClose)
    EMA_Above_BB_Ready = EMA_Above_BB(candlesClose)
    EMA_Ready = EMA(candlesClose)
    BB_LowestBelowLowerCloseAboveLower_Ready = BB_LowestBelowLowerCloseAboveLower(candlesClose, candlesLowest)
    MFI_Ready = MFI(candlesHighest, candlesLowest, candlesClose, candlesVolume)
    MOM_Ready = MOM(candlesClose)
    MACD_Ready = MACD(candlesClose)
    SMA_TodayCloseAboveBeforeClose_Ready = SMA_TodayCloseAboveBeforeClose(candlesClose)
    # GREEN_Ready = GREEN(candlesClose)
    SMA_RSI_Ready = SMA_RSI(candlesClose)

    if SMA_TodayCloseAboveBeforeClose_Ready and SMA_RSI_Ready and RSI_Ready and\
        (OBV_Ready or MACD_Uptrend or \
            EMA_Above_BB_Ready or EMA_Ready or \
                BB_LowestBelowLowerCloseAboveLower_Ready or \
                    MFI_Ready or MOM_Ready or MACD_Ready):
        return app.cryptoToTrade
    else:
        return None

# def GREEN(close):
#     if close[-1] > close[-2]:
#         return True

def BB_LowestBelowLowerCloseAboveLower(close, low):
    upperBB, middleBB, lowerBB = talib.BBANDS(close, timeperiod=app.timePeriodForBB, nbdevup=2, nbdevdn=2, matype=0)

    if low[-1] <= lowerBB[-1] and close[-1] >= lowerBB[-1]:
        return True

def EMA(close):
    EMAsFast = talib.EMA(close, timeperiod=9)
    EMAsSlow = talib.EMA(close, timeperiod=20)

    if EMAsFast[-1] >= EMAsSlow[-1]:
        return True

def EMA_Above_BB(close):
    EMAs = talib.EMA(close, timeperiod=20)
    upperBB, middleBB, lowerBB = talib.BBANDS(close, timeperiod=app.timePeriodForBB, nbdevup=app.nbDev, nbdevdn=app.nbDev, matype=0)

    if EMAs[-1] >= middleBB[-1]:
        return True

def SMA_RSI(close):
    RSIs = talib.RSI(close, timeperiod=14)
    SMAs = talib.SMA(RSIs, timeperiod=14)
   
    if 70 > RSIs[-1] > SMAs[-1]:
        return True

def SMA_TodayCloseAboveBeforeClose(close):
    the72 = (72 * 60) / 15
    SMAs = talib.SMA(close, timeperiod=the72)

    if SMAs[-1] < close[-1]:
        return True

def OBV(candlesClose, candlesVolume):
    OBVs = talib.OBV(candlesClose, candlesVolume)

    if OBVs[-2] < OBVs[-1]:
        return True

def RSI(close):
    RSIs = talib.RSI(close, timeperiod=14)
    
    if 70 > RSIs[-1] > RSIs[-2]:
        return True
    
def RSI_Overbought(close):
    RSIs = talib.RSI(close, timeperiod=14)
    
    if 70 <= RSIs[-1]:
        return True
    
# def RSI_Above50(close):
#     RSIs = talib.RSI(close, timeperiod=14)
    
#     if 50 <= RSIs[-1]:
#         return True
  
def MACD(close):
    macd, signal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[-2] < macd[-1]:
        return True
    
def MACD_Divergence_Uptrend(close):
    macd, signal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[-5] < macd[-1]:
        return True 
    
def MACD_Divergence_Downtrend(close):
    macd, signal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    if macd[-3] > macd[-1]:
        return True 
    
def MOM(close):
    MOMs = talib.MOM(close, timeperiod=5)
    currentMOM = MOMs[-1]

    if currentMOM > 0:
        return True
    
def MFI(high, low, close, volume):
    MFIs = talib.MFI(high, low, close, volume, timeperiod=14)

    if MFIs[-1] <= 20:
        return True