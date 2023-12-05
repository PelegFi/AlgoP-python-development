import TradingApp
import pandas as pd
import numpy as np
import indicators
from copy import deepcopy
import openpyxl
from excels import Excels
from Utilities import Utilities

def backtest_strategy1(tradingApp:TradingApp,strategy_vars:dict):
        #setting up variabels
        contracts = strategy_vars["contracts"]
        backtest_vars = strategy_vars["backtest_vars"]
        risk_vars = strategy_vars["risk_vars"]
        strategy_parameters = strategy_vars["strategy_vars"]
        other_vars = strategy_vars["other_variables"]
        strategy_func = strategy_vars["strategy_function"]
        result={} # resaul dictionary
        excel = Excels(other_vars["excle_path_backtest"])
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
                result[ticker] = {}

        #BACKTEST PART
        for ticker in dataFramesDict.keys():
                #setting up variables for comfort writing
                print(f"==================== BACKTESTING {ticker} ====================")
                current_position=""
                current_return= []
                current_tradeCount=0
                current_start_price = None
                current_end_price = None
                current_dataFrame=dataFramesDict[ticker]
                #create a new excel sheet 
                excel.wb.create_sheet(ticker)
                excel.current_ws = excel.wb[ticker]
                excel.create_strategy1_excel()

                for i in range(1,len(current_dataFrame)):
                        #setting up variables for comfort writing
                        current_Zscore = current_dataFrame["Zscore"].iloc[i]
                        current_emaZ= current_dataFrame["emaZ"].iloc[i]
                        current_price=current_dataFrame["close"].iloc[i]
                        current_date=current_dataFrame.index[i]
                        current_signal=strategy_func(current_Zscore,current_emaZ)

                        if current_position == "":
                                if current_signal == "BUY":
                                        current_position="BUY"
                                        current_tradeCount+=1
                                        current_start_price=current_price
                                        print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                        excel.write_line_backtest_strategy1(current_date,current_price,"BUY",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))
                                elif current_signal == "SELL" :
                                        current_position="SELL"
                                        current_tradeCount+=1
                                        current_start_price=current_price
                                        print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                        excel.write_line_backtest_strategy1(current_date,current_price,"SELL",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))
                        else :
                                if current_position == "BUY":
                                        if current_signal == "SELL":
                                                #calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")

                                                # GO SHORT 
                                                current_position="SELL"
                                                current_tradeCount+=1
                                                current_start_price = current_price
                                                print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                                excel.write_line_backtest_strategy1(current_date,current_price,"SELL",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))
                                        elif current_signal == "":
                                                #close BUY position + calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                current_tradeCount += 1
                                                current_position = ""
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                                excel.write_line_backtest_strategy1(current_date,current_price,"SELL",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))
                                elif current_position == "SELL":
                                        if current_signal == "BUY":
                                                #calculate sell trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")

                                                # GO long 
                                                current_position="BUY"
                                                current_tradeCount+=1
                                                current_start_price = current_price
                                                print(f"OPEN TRADE : {current_position} || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                                excel.write_line_backtest_strategy1(current_date,current_price,"BUY",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))
                                        elif current_signal == "":
                                                #close SELL position + calculate buy trade profit
                                                current_end_price = current_price
                                                current_return.append(Utilities.calculate_profit_percentage(current_start_price,current_end_price,current_position))
                                                current_tradeCount += 1
                                                current_position = ""
                                                print(f"CLOSE TRADE || PRICE : {current_price} || DATE : {current_date} || STRATEGY SIGNAL : {current_signal} || Zscore : {current_Zscore} || emaZ : {current_emaZ}")
                                                excel.write_line_backtest_strategy1(current_date,current_price,"BUY",current_signal,current_Zscore,current_emaZ,sum(current_return),Utilities.calculate_compound_returns(current_return))

                #SAVING THE RSULTS INTO DICT
                result[ticker]["returns"] = current_return
                result[ticker]["trade_count"] = current_tradeCount
                result[ticker]["compound_returns"] = Utilities.calculate_compound_returns(result[ticker]["returns"])
                result[ticker]["volatility"] = Utilities.volatility(np.array(result[ticker]["returns"]))
                parts=backtest_vars["backtest_time"].split(' ')
                if parts[1] == "Y":
                        result[ticker]["CAGR"] = Utilities.CAGR(np.array(result[ticker]["compound_returns"]),int(parts[0]))
                        result[ticker]["SHARPE_ANNUAL"] = Utilities.sharpe_ratio_annualize(result[ticker]["CAGR"],2.5,result[ticker]["volatility"])
                print("\n")
        
        Utilities.print_backtest_result(result)
                        







