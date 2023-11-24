import TradingApp
import pandas as pd
import numpy as np
import indicators
from copy import deepcopy
import Utilities

def backtest_strategy1(tradingApp:TradingApp,strategy_vars:dict):
        #setting up variabels
        print(strategy_vars)
        contracts = strategy_vars["contracts"]
        backtest_vars = strategy_vars["backtest_vars"]
        risk_vars = strategy_vars["risk_vars"]
        strategy_parameters = strategy_vars["strategy_vars"]  # Use a different variable name
        other_vars = strategy_vars["other_variables"]
        strategy_func = strategy_vars["strategy_function"]

        #results dits 
        ticker_returns={}#->{"ticker":list} | storing returns for eachh tickers
        ticker_tradeCount={}#->{"ticker":int} | storing tradecount for each ticker 
        ticker_compoundReturns ={}
        result={}

        #requesting historical data for contracts
        tradingApp.reqHistData(contracts,backtest_vars["end_date"],backtest_vars["backtest_time"],strategy_parameters["candlesTimeFrame"])
        dataFramesDict=deepcopy(tradingApp.historicalDataFrame)

        #INITIATING DATAFRAME + DICTS 
        for ticker in dataFramesDict.keys():
                #Adding up relevant indicators to the Dataframe
                dataFramesDict[ticker] = indicators.Zscore(dataFramesDict[ticker],strategy_parameters["ZscoreWindow"],strategy_parameters["emaZwindow"])
                dataFramesDict[ticker]["ATR"] = indicators.ATR(dataFramesDict[ticker],14)
                dataFramesDict[ticker]["RSI"] = indicators.RSI(dataFramesDict[ticker],21)
                dataFramesDict[ticker].dropna(inplace=True)

        #BACKTEST PART
        for ticker in dataFramesDict.keys():
                #setting up variables for comfort writing
                current_position=""
                current_return= []
                current_tradeCount=0
                current_start_price = None
                current_end_price = None

                for i in range(1,len(dataFramesDict[ticker])):
                        #setting up variables for comfort writing
                        current_Zscore = dataFramesDict["Zscore"][i]
                        current_emaZ= dataFramesDict["emaZ"][i]
                        current_price=dataFramesDict["close"][i]
                        current_date=dataFramesDict["date"][i]
                        current_signal=strategy_func(current_Zscore,current_emaZ)

                        if current_position == "":
                                if current_signal == "BUY":
                                        current_position="BUY"
                                        current_tradeCount+=1
                                        current_start_price=current_price
                                        print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")
                                elif current_signal == "SELL" :
                                        current_position="SELL"
                                        current_tradeCount+=1
                                        current_start_price=current_price
                                        print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")
                        else :
                                if current_position == "BUY":
                                        if current_signal == "SELL":
                                                #calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")

                                                # GO SHORT 
                                                current_position="SELL"
                                                current_tradeCount+=1
                                                current_start_price = current_price
                                                print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")
                                        elif current_signal == "":
                                                #close BUY position + calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                current_tradeCount += 1
                                                current_position = ""
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")
                                elif current_position == "SELL":
                                        if current_signal == "BUY":
                                                #calculate sell trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")

                                                # GO long 
                                                current_position="BUY"
                                                current_tradeCount+=1
                                                current_start_price = current_price
                                                print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")
                                        elif current_signal == "":
                                                #close SELL position + calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                current_tradeCount += 1
                                                current_position = ""
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal}")


                result[ticker]["returns"] = current_return
                result[ticker]["trade_count"] = current_tradeCount
                result[ticker]["compound_returns"] = Utilities.calculate_compound_returns(result[ticker]["returns"])
                result[ticker]["volatility"] = Utilities.volatility(np.array(result[ticker]["returns"]))
                parts=backtest_vars["backtest_time"].split(' ')
                if parts[1] == "Y":
                        result[ticker]["CAGR"] = Utilities.CAGR(np.array(result[ticker]["compound_returns"]),int(parts[0]))
                        result[ticker]["SHARPE_ANNUAL"] = Utilities.sharpe_ratio_annualize(result[ticker]["CAGR"],2.5,result[ticker]["volatility"])
        
        print(result)
                        






