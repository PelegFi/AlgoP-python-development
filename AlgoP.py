
from TradingApp import TradingApp
import Utilities as u
import configStrategy1 as c
import time
import threading
from indicators import Indicators

#intiating app
AlgoP = TradingApp()
####################################################################
AlgoP.reqHistData(c.contracts,"","1 M","30 mins")
print(AlgoP.historicalDataFrame)
macd=Indicators.MACD(AlgoP.historicalDataFrame["AAPL"],26,12,9,True)