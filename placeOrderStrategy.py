import TradingApp
from Utilities import Utilities
import pandas as pd
import time
import copy
import indicators
import datetime
from excels import Excels

def strategy_1 (tradingApp:TradingApp,strategy_vars:dict,openPositions:dict,account_summery:pd.DataFrame):
   #setting up variabels
   contracts = strategy_vars["contracts"] #-> contracts dictionary not contract objects !
   risk_vars = strategy_vars["risk_vars"]
   strategy_parameters = strategy_vars["strategy_vars"]
   other_vars = strategy_vars["other_variables"]
   strategy_func = strategy_vars["strategy_function"]
   account_name=strategy_vars["accounts_list"][0]
   positions_data= openPositions[account_name].to_dict(orient='index') if openPositions is not None else {} #-> dict {ticker :{position : "BUY/SELL/""" ,amount : int ,start_price : float}}
   excel = Excels(other_vars["live_excel_path"])
   returns = {} #-> {ticker : []}

   #requesting historical data for first calc + get socket connections
   tradingApp.reqHistData(contracts,"",Utilities.calc_backtest_min_time(),strategy_parameters["candlesTimeFrame"])
   data_df_dict=copy.deepcopy(tradingApp.historicalDataFrame)#-> {ticker : dataframe }

   #preperations for strategy loop 
   for contract in contracts:
      #requesting market data socket connection
      tradingApp.reqMktData(contracts.index(contract),Utilities.createContract(contract["symbol"],contract["secType"],contract["currency"],contract["exchange"]),"",False,False,[])
      #initiate current position dict 
      if contract["symbol"] not in positions_data :
         positions_data[contract["symbol"]] = {"position":"","amount":0,"start_price":None}
      #creating new excek sheet 
      excel.wb.create_sheet(contract["symbol"])
      excel.current_ws = excel.wb[contract["symbol"]]
      excel.create_strategy1_excel()
      #intiating returns
      returns[contract["symbol"]] = []

   time.sleep(10)
   counter_delete = 1

   #the strategy loop 
   while True : 
      print("*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=* NEW BIG LOOP =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=")
      #intiating loop start time 
      loop_start_time = time.time()
      formatted_time = Utilities.fromat_dateTime(loop_start_time)

      #calculate capital for current loop (accountnetliq / precentage_from_capital )
      print(f"account summery ==== {account_summery[account_name]} ||| {account_summery[account_name].loc["NetLiquidationByCurrency","Value"]} ||| {type(account_summery[account_name].loc["NetLiquidationByCurrency","Value"])} || formatted time === {formatted_time} || formated time type = {type(formatted_time)}")
      net_liq_value = account_summery[account_name].loc["NetLiquidationByCurrency", "Value"]
      if isinstance(net_liq_value, pd.Series):
         net_liq_value = net_liq_value.iloc[-1]
      capital = float(net_liq_value) * (risk_vars["precentage_from_capital"] / 100)

      

      #removing last row price and adding new row with current price 
      for contract in contracts :
         data_df_dict[contract["symbol"]] = data_df_dict[contract["symbol"]]._append(pd.DataFrame({"open":None,"high":None,"low":None,"close":tradingApp.tick_price_dict[contract["symbol"]],"volume":None},index = [formatted_time]))#adding the new row with current price
         data_df_dict[contract["symbol"]] = data_df_dict[contract["symbol"]].iloc[1:] #removing
      

      while Utilities.time_in_loop(strategy_parameters["candlesTimeFrame"],loop_start_time):
         for contract in contracts :
            #set initial loop vars 
            current_contract = Utilities.createContract(contract["symbol"],contract["secType"],contract["currency"],contract["exchange"])
            current_symbol= current_contract.symbol
            current_price=tradingApp.tick_price_dict[current_symbol]
            quantity = int (capital/current_price)
            positions_data_symbol =  positions_data[current_symbol]

            #changin excel sheet 
            excel.current_ws = excel.wb[current_symbol]

            #add the last price and preform real time calc
            data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1], "close"] = current_price
            data_df_dict[current_symbol] = indicators.Zscore(data_df_dict[current_symbol],strategy_parameters["ZscoreWindow"],strategy_parameters["emaZwindow"])
            current_signal=strategy_func(data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"])
            
            #delete after debugging
            print(f"for loop number {counter_delete} , ticker {current_symbol} || CAPITAL = {capital} || quantity : {quantity} || dataframe : {data_df_dict[current_symbol]}")
            print(f"current signal : {current_signal} || current positions for -> {current_symbol} : {positions_data_symbol}")
            counter_delete+=1

            #the strategy part 
            if positions_data_symbol["position"] == "":
               if current_signal == "BUY":
                  Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",quantity))
                  positions_data_symbol.update({"position" : "BUY" , "amount" : quantity , "start_price" : current_price})
                  print(f"SYMBOL : {current_symbol} || CURRENT ACTION : BUY || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity}")
                  excel.write_line_backtest_strategy1(formatted_time,current_price,"BUY",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
               elif current_signal == "SELL":
                  Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",quantity))
                  positions_data_symbol.update({"position" : "SELL" , "amount" : quantity , "start_price" : current_price})
                  print(f"SYMBOL : {current_symbol} || CURRENT ACTION : SELL || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity}")
                  excel.write_line_backtest_strategy1(formatted_time,current_price,"SELL",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
            else :
               if positions_data_symbol["position"] == "BUY":
                  if current_signal == "SELL":
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",quantity+positions_data_symbol["amount"]))
                     returns[current_symbol].append(Utilities.calculate_profit_percentage(positions_data_symbol["start_price"], current_price, positions_data_symbol["position"]))
                     print("real_returns_precentages !!!!!!!!!!!! ",returns[current_symbol])
                     positions_data_symbol.update({"position" : "SELL" , "amount" : -quantity , "start_price" : current_price})
                     print(f"SYMBOL : {current_symbol} || CURRENT ACTION : SELL || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity+positions_data_symbol["amount"]}")
                     excel.write_line_backtest_strategy1(formatted_time,current_price,"SELL",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
                  elif current_signal == "":
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",positions_data_symbol["amount"]))
                     returns[current_symbol].append(Utilities.calculate_profit_percentage(positions_data_symbol["start_price"], current_price, positions_data_symbol["position"]))
                     print("real_returns_precentages !!!!!!!!!!!! ",returns[current_symbol])
                     positions_data_symbol.update({"position" : "" , "amount" : 0 , "start_price" : None })
                     print(f"SYMBOL : {current_symbol} || CURRENT ACTION : SELL || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {positions_data_symbol["amount"]}")
                     excel.write_line_backtest_strategy1(formatted_time,current_price,"SELL",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
               elif positions_data_symbol["position"] == "SELL":
                  if current_signal == "BUY":
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",quantity+abs(positions_data_symbol["amount"])))
                     print(f"SYMBOL : {current_symbol} || CURRENT ACTION : BUY || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity+positions_data_symbol["amount"]}")
                     returns[current_symbol].append(Utilities.calculate_profit_percentage(positions_data_symbol["start_price"], current_price, positions_data_symbol["position"]))
                     print("real_returns_precentages !!!!!!!!!!!! ",returns[current_symbol])
                     positions_data_symbol.update({"position" : "BUY" , "amount" : quantity , "start_price" : current_price})
                     excel.write_line_backtest_strategy1(formatted_time,current_price,"BUY",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
                  elif current_signal == "":
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",abs(positions_data_symbol["amount"])))
                     print(f"SYMBOL : {current_symbol} || CURRENT ACTION : BUY || SIGNAL : {current_signal} || PRICE : {current_price} || QUANTITY : {positions_data_symbol["amount"]}")
                     returns[current_symbol].append(Utilities.calculate_profit_percentage(positions_data_symbol["start_price"], current_price, positions_data_symbol["position"]))
                     print("real_returns_precentages !!!!!!!!!!!! ",returns[current_symbol])
                     positions_data_symbol.update({"position" : "" , "amount" : 0 , "start_price" : None})
                     excel.write_line_backtest_strategy1(formatted_time,current_price,"BUY",current_signal,data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"Zscore"],data_df_dict[current_symbol].loc[data_df_dict[current_symbol].index[-1],"emaZ"],sum(returns[current_symbol]),Utilities.calculate_compound_returns(returns[current_symbol]))
            
            #print current p&l
            if positions_data_symbol["position"] != "":
               print(F"THE  CURRENT P&L FOR TICKER : {current_symbol} IS -> {Utilities.calculate_profit_percentage(positions_data_symbol["start_price"],current_price,positions_data_symbol["position"])} %")

            #Sleep for 1 min
            time.sleep(19)
