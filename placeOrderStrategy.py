import TradingApp
import pandas as pd

def strategy_1 (tradingApp:TradingApp,strategy_vars:dict,openPositions:dict,account_summery:pd.DataFrame):
     #setting up variabels
        contracts = strategy_vars["contracts"]
        risk_vars = strategy_vars["risk_vars"]
        strategy_parameters = strategy_vars["strategy_vars"]
        other_vars = strategy_vars["other_variables"]
        strategy_func = strategy_vars["strategy_function"]
        current_positions ={} #-> {ticker : {position : int , avg_cost : float}}

        #setting up existing positions

        
        
        #requesting historical data for first calc + get socket connections
        print(account_summery)
        print(openPositions)