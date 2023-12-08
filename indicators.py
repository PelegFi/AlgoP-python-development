import pandas as pd
import numpy as np
from Utilities import Utilities

################################# ALL INDICATORS #########################

def MACD(detaFrame:pd,MACDslow:int,MACDfast:int,signalLineWindow:int,exponential:bool):
    df=detaFrame.copy()
    if exponential==False:
        df["MA_fast"] = df["close"].rolling(MACDfast).mean()
        df["MA_slow"] = df["close"].rolling(MACDslow).mean()
        df["MACD"] = df["MA_fast"]-df["MA_slow"]
        df["singal_line"] = df["MACD"].rolling(signalLineWindow).mean()
        return df 
    else :
        df["MA_fast"] = df["close"].ewm(span=MACDfast,min_periods=MACDslow).mean()
        df["MA_slow"] = df["close"].ewm(span=MACDslow,min_periods=MACDslow).mean()
        df["MACD"] = df["MA_fast"]-df["MA_slow"]
        df["singal_line"] = df["MACD"].ewm(span=signalLineWindow,min_periods=signalLineWindow).mean()
        return df 
    
def bollinger_bands(detaFrame:pd,MA_window:int,standart_deviation_multiplyer:int,exponential:bool):
    df=detaFrame.copy()

    if exponential == False:
        df["MA"] = df["close"].rolling(MA_window).mean()
    else :
        df["MA"] = df["close"].ewm(span=MA_window,min_periods=MA_window).mean()

    df["BB_up"] = df["MA"] + standart_deviation_multiplyer*df["close"].rolling(MA_window).std(ddof=0)
    df["BB_down"] = df["MA"] - standart_deviation_multiplyer*df["close"].rolling(MA_window).std(ddof=0)
    df["BB_width"] = df["BB_up"] - df["BB_down"]
    df.dropna(inplace=True)

    return df

def ATR(dataFrame: pd.DataFrame, window: int):
    df = dataFrame.copy()

    df["high-low"] = abs(df['high'] - df['low'])
    df["high-previousClose"] = abs(df["high"] - df["close"].shift(1))
    df["low-previousClose"] = abs(df["low"] - df["close"].shift(1))
    
    df["true_range"] = df[["high-low", "high-previousClose", "low-previousClose"]].max(axis=1)

    df['ATR'] = df["true_range"].ewm(span=window, min_periods=window).mean()
    return df['ATR']

def RSI(DF,n):
    "function to calculate RSI"
    df = DF.copy()
    df['delta']=df['close'] - df['close'].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0)
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
           avg_gain.append(df['gain'].rolling(n).mean().iloc[n])
           avg_loss.append(df['loss'].rolling(n).mean().iloc[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100/(1+df['RS']))
    return df['RSI']

def ADX(dataFrame: pd.DataFrame, window: int):
    #average directional index

    df = dataFrame.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['+DM']=np.where((df['High']-df['High'].shift(1))>(df['Low'].shift(1)-df['Low']),df['High']-df['High'].shift(1),0)
    df['+DM']=np.where(df['+DM']<0,0,df['+DM'])
    df['-DM']=np.where((df['Low'].shift(1)-df['Low'])>(df['High']-df['High'].shift(1)),df['Low'].shift(1)-df['Low'],0)
    df['-DM']=np.where(df['-DM']<0,0,df['-DM'])

    df["+DMMA"]=df['+DM'].ewm(span=window,min_periods=window).mean()
    df["-DMMA"]=df['-DM'].ewm(span=window,min_periods=window).mean()
    df["TRMA"]=df['TR'].ewm(span=window,min_periods=window).mean()

    df["+DI"]=100*(df["+DMMA"]/df["TRMA"])
    df["-DI"]=100*(df["-DMMA"]/df["TRMA"])
    df["DX"]=100*(abs(df["+DI"]-df["-DI"])/(df["+DI"]+df["-DI"]))
    
    df["ADX"]=df["DX"].ewm(span=window,min_periods=window).mean()

    return df['ADX']      

def Zscore(dataFrame:pd.DataFrame,ZscoreWindow,MAwindow) :
    df=dataFrame.copy()
    df["Zscore"]=(df["close"]-df["close"].rolling(ZscoreWindow).mean())/df["close"].rolling(ZscoreWindow).std(ddof=0)
    df["smaZ"]=df["Zscore"].rolling(MAwindow).mean()

    return df

def calculate_fibonacci_levels(high, low):
    fibonacci_levels = {}
    difference = high - low

    fibonacci_levels["38.2%"] = high - difference * 0.382
    fibonacci_levels["50%"] = high - difference * 0.5
    fibonacci_levels["61.8%"] = high - difference * 0.618

    return fibonacci_levels


    decimal_returns=utilities.returns_precentage_to_decimal(precentage_returns)
    compundPnL=utilities.calculate_compound_returns(decimal_returns)
    annualize_return= compundPnL**1/years - 1
    return annualize_return
