#############################strategy 1 variables ###################################
def strategy1(Zscore,emaZ)-> str:
    if Zscore>0 and Zscore>emaZ:
        return "BUY"
    elif Zscore<0 and Zscore<emaZ:
        return "SELL"
    else:
        return ""
    
backtest_vars={
               "backtest_time":"2 M",
               "end_date":""}

contracts = [{"symbol":"TQQQ","secType":"STK","currency":"USD","exchange":"SMART"},
           {"symbol":"SSO","secType":"STK","currency":"USD","exchange":"SMART"}
           ]

risk_vars={"precentage_from_capital":5,
           "maximum_risk_precentage":10}

strategy_vars={"ZscoreWindow":75,
               "emaZwindow":75,
               "candlesTimeFrame":"15 mins"}

other_vars={"excel_file_path" : "C:\\Users\\Administrator\\Desktop\\output.xlsx"}

#############################strategy 2 variables ###################################


#sending all of the vars 
all_vars={"strategy 1":
          {"strategy_function":strategy1,
           "backtest_vars":backtest_vars,
           "contracts":contracts,
           "risk_vars":risk_vars,
           "strategy_vars":strategy_vars,
           "other_variables":other_vars}}