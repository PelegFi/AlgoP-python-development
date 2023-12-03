import TradingApp
from utilities import Utilities
import pandas as pd
import time
import copy
import indicators
import datetime

def strategy_1 (tradingApp:TradingApp,strategy_vars:dict,openPositions:dict,account_summery:pd.DataFrame):
   #setting up variabels
   contracts = strategy_vars["contracts"] #-> contracts dictionary not contract objects !
   risk_vars = strategy_vars["risk_vars"]
   strategy_parameters = strategy_vars["strategy_vars"]
   other_vars = strategy_vars["other_variables"]
   strategy_func = strategy_vars["strategy_function"]
   account_name=strategy_vars["accounts_list"][0]
   capital = float(account_summery[account_name].loc["NetLiquidationByCurrency","Value"]) * (risk_vars["precentage_from_capital"]/100) 
   current_positions= openPositions[account_name].to_dict(orient='index') if openPositions is not None else {} #-> dict {ticker :{position : "BUY/SELL/""" ,amount : int ,start_price : float}}
  

   #requesting historical data for first calc + get socket connections
   tradingApp.reqHistData(contracts,"",Utilities.calc_backtest_min_time(),strategy_parameters["candlesTimeFrame"])
   data_df_dict=copy.deepcopy(tradingApp.historicalDataFrame)#-> {ticker : dataframe }

   #preperations for strategy loop 
   for contract in contracts:
      current_symbol1 = contract["symbol"]

      #requesting market data socket connection
      tradingApp.reqMktData(contracts.index(contract),Utilities.createContract(current_symbol1,contract["secType"],contract["currency"],contract["exchange"]),"",False,False,[])

      #initiate current position dict 
      if current_symbol1 not in current_positions :
         current_positions[current_symbol1] = {"position":"","amount":0,"start_price":None}

   #the strategy loop 
   while True : 
      #intiating loop start time 
      loop_start_time=time.time()
      dt_object = datetime.fromtimestamp(loop_start_time)
      formatted_time = dt_object.strftime("%Y%m%d %H:%M:%S")

      #removing last row price and adding new row with current price 
      for contract in contracts :
         data_df_dict[contract["symbol"]]._append(pd.DataFrame({"date":formatted_time,"open":None,"high":None,"low":None,"close":tradingApp.tick_price_dict[current_symbol],"volume":None}))#adding the new row with current price
         data_df_dict[contract["symbol"]] = data_df_dict[current_symbol].iloc[1:] #removing

      while Utilities.time_in_loop(strategy_parameters["candlesTimeFrame"],loop_start_time):
         for contract in contracts :
            #set initial loop vars 
            current_contract = Utilities.createContract(contract["symbol"],contract["secType"],contract["currency"],contract["exchange"])
            current_symbol=current_contract.symbol
            current_price=tradingApp.tick_price_dict[current_symbol]
            quantity = int (capital/current_price)

            #add the last price and preform real time calc
            data_df_dict[current_symbol].iloc[-1,"close"] = current_price
            data_df_dict[current_symbol].iloc[-1,"date"] = formatted_time
            data_df_dict[current_symbol] = indicators.Zscore(data_df_dict[current_symbol],strategy_parameters["ZscoreWindow"],strategy_parameters["emaZwindow"])
            data_df_dict[current_symbol].dropna(inplace=True)
            current_signal=strategy_func(data_df_dict[current_symbol].iloc[-1,"Zscore"],data_df_dict[current_symbol].iloc[-1,"emaZ"])
            
            #the strategy part 
            if current_positions[current_symbol]["position"] == "":
               if current_signal == "BUY":
                  current_positions[current_symbol].update({"position" : "BUY" , "amount" : quantity , "start_price" : current_price})
                  Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",quantity))
                  print(f"SYMBOL : {current_symbol} || ACTION : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity}")
               elif current_signal == "SELL":
                  current_positions[current_symbol].update({"position" : "SELL" , "amount" : quantity , "start_price" : current_price})
                  Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",quantity))
                  print(f"SYMBOL : {current_symbol} || ACTION : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity}")
            else :
               if current_positions[current_symbol]["position"] == "BUY":
                  if current_signal == "SELL":
                     current_positions[current_symbol].update({"position" : "SELL" , "amount" : quantity+current_positions[current_symbol]["amount"], "start_price" : current_price})
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",quantity+current_positions[current_symbol]["amount"]))
                     print(f"SYMBOL : {current_symbol} || ACTION : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity+current_positions[current_symbol]["amount"]}")
                  elif current_signal == "":
                     current_positions[current_symbol].update({"position" : "" , "amount" : 0 , "start_price" : None})
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("SELL",current_positions[current_symbol]["amount"]))
                     print(f"SYMBOL : {current_symbol} || ACTION : SELL || PRICE : {current_price} || QUANTITY : {current_positions[current_symbol]["amount"]}")
               elif current_positions[current_symbol]["position"] == "SELL":
                  if current_signal == "BUY":
                     current_positions[current_symbol].update({"position" : "BUY" , "amount" : quantity+current_positions[current_symbol]["amount"], "start_price" : current_price})
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",quantity+current_positions[current_symbol]["amount"]))
                     print(f"SYMBOL : {current_symbol} || ACTION : {current_signal} || PRICE : {current_price} || QUANTITY : {quantity+current_positions[current_symbol]["amount"]}")
                  elif current_signal == "":
                     current_positions[current_symbol].update({"position" : "" , "amount" : 0 , "start_price" : None})
                     Utilities.place_order(tradingApp,current_contract,Utilities.market_order("BUY",current_positions[current_symbol]["amount"]))
                     print(f"SYMBOL : {current_symbol} || ACTION : BUY || PRICE : {current_price} || QUANTITY : {current_positions[current_symbol]["amount"]}")
            
            #print current p&l
            if current_positions[current_symbol]["position"] != "":
               print(F"THE  CURRENT P&L FOR TICKER : {current_symbol} IS -> {Utilities.calculate_profit_percentage(current_positions[current_symbol]["start_price"],current_price,current_positions[current_symbol]["position"])}")

