import threading
from ibapi.client import *
from ibapi.wrapper import *
import time , Utilities 
from config_strategys import all_vars 
import pandas as pd
import warnings
import backtests , placeOrderStrategy

class TradingApp(EWrapper, EClient):
    def __init__(self):
        ######################## varibels ####################
        self.historicalDataFrame = {} #-> should be {"ticker":dataFrame}
        self.historicalDataCounter = -1
        self.is_position_arrived=False
        self.is_account_summary_arrived = False
        # self.nextValidOrderId -> been initiated in method 'nextValidId'
        self.orders_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                              'Account', 'Symbol', 'SecType',
                                              'Exchange', 'Action', 'OrderType',
                                              'TotalQty', 'CashQty', 'LmtPrice',
                                              'AuxPrice', 'Status'])
        self.current_positions ={}#-> {"symbol" : {account : ,sectype: ,currency: position_size: ,avg_cost: }}
        self.account_summary = {}#-> {account : dataframe}
        self.pnl_summary = pd.DataFrame(columns=['ReqId', 'DailyPnL', 'UnrealizedPnL', 'RealizedPnL'])
        ######################## connecting to TWS ####################
        EClient.__init__(self, wrapper=self)
        self.connect("127.0.0.1", 7497, clientId=0)
        time.sleep(5)
        #running EREADER thread 
        def websocket_connection():
            self.run()
        socket_thread=threading.Thread(target=websocket_connection)# creating new thread for Ereader ti recive all the messages 
        socket_thread.start()
        time.sleep(1)
########################## EWRAPPER IMPLANTS #######################################
    def error(self, reqId, errorCode, errorString):
        print("Error {}: {}".format(errorCode, errorString))
    
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        time.sleep(1)

    def contractDetails(self, reqId, contractDetails):
        print("req id: {}, contract: {}".format(reqId, contractDetails))
    
    def historicalData(self, reqId: int, bar: BarData):
        #arranging historical data in a data stracture 
        if all_vars[current_strategy_name]["contracts"][reqId]["symbol"] not in self.historicalDataFrame.keys() : 
            self.historicalDataFrame[all_vars[current_strategy_name]["contracts"][reqId]["symbol"]] = [{"date":bar.date,"open":bar.open,"high":bar.high,"low":bar.low,"close":bar.close,"volume":bar.volume}]
        elif all_vars[current_strategy_name]["contracts"][reqId]["symbol"] in self.historicalDataFrame.keys() : 
            self.historicalDataFrame[all_vars[current_strategy_name]["contracts"][reqId]["symbol"]].append({"date":bar.date,"open":bar.open,"high":bar.high,"low":bar.low,"close":bar.close,"volume":bar.volume})
        
        #printing the data for user 
        print (f"historical data reqID : {reqId} \n BarData : {bar}")
    
    def historicalDataEnd(self, reqId:int, start:str, end:str):
        """ Marks the ending of the historical bars reception. """
        self.logAnswer(current_fn_name(), vars())
        self.historicalDataCounter = self.historicalDataCounter+1
        print(f"self historical data counter = {self.historicalDataCounter}")
        
    def openOrder(self, orderId, contract, order, orderState):
        # To suppress the warning
        warnings.filterwarnings("ignore", message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.")    
        super().openOrder(orderId, contract, order, orderState)
        dictionary = {"PermId":order.permId, "ClientId": order.clientId, "OrderId": orderId, 
                      "Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Exchange": contract.exchange, "Action": order.action, "OrderType": order.orderType,
                      "TotalQty": order.totalQuantity, "CashQty": order.cashQty, 
                      "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
        self.orders_df = self.orders_df._append(dictionary, ignore_index=True)
    
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)

        if account not in self.current_positions:
            self.current_positions[account] = pd.DataFrame(columns=["contract","position","avg_cost"]).set_index("contract")
        
        self.current_positions[account] = self.current_positions[account]._append(pd.DataFrame({"position":position,"avg_cost":avgCost},index=[contract.symbol]))
        # Set the flag to indicate the new position data has arrived
        self.is_position_arrived = True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        super().accountSummary(reqId, account, tag, value, currency)

        if account not in self.account_summary:
            self.account_summary[account] = pd.DataFrame(columns=["Tag","Value"]).set_index("Tag")
        
        self.account_summary[account]=self.account_summary[account]._append(pd.DataFrame({"Value":value},index=[tag]))
        self.is_account_summary_arrived=True
        
    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
        dictionary = {"ReqId":reqId, "DailyPnL": dailyPnL, "UnrealizedPnL": unrealizedPnL, "RealizedPnL": realizedPnL}
        self.pnl_summary = self.pnl_summary._append(dictionary, ignore_index=True)

    def tickPrice(self, tickerId, field, price, attrib):
        print(f"Ticker Id: {tickerId}, Field: {field}, Price: {price}")

########################## MY FUNCTIONS  ####################################### 
    def play(self,strategy_name:str,backtestMode:bool):
        self.reqPositions()
        self.reqAccountSummary(9002, "All", "$LEDGER")

        while self.is_position_arrived == False or self.is_account_summary_arrived== False :
            time.sleep(1)

        if backtestMode :
            if strategy_name == "strategy 1":
                backtests.backtest_strategy1(self,all_vars[strategy_name])
        else:
            if strategy_name == "strategy 1":
                placeOrderStrategy.strategy_1(self,all_vars[strategy_name],self.current_positions,self.account_summary)
               
    def reqHistData(self,contracts : list,endDate:str,duration:str,candleTimeFrame:str) -> None :
        # requesting historical market data for at list of contracts + storing the data into pandas dataframe dictionary
        #ANY financial instumeent can be ADDED@!!! in this case i have added only "cash" + "stk"
        #requesting the historical market data :
        counter=0
        for contract in contracts :
            if contract["secType"]=="STK":
                self.reqHistoricalData(counter,Utilities.createContract(contract["symbol"],contract["secType"],contract["currency"],contract["exchange"]),endDate,duration,candleTimeFrame,"TRADES",1,1,False,[])
            elif contract["secType"]=="CASH":
                self.reqHistoricalData(counter,Utilities.createContract(contract["symbol"],contract["secType"],contract["currency"],contract["exchange"]),endDate,duration,candleTimeFrame,"MIDPOINT",1,1,False,[])
            
            #waiting for historical data to be recived before requesting historical for another contract 
            while int(self.historicalDataCounter) != counter :
                print(f"waiting for historical data for contract {contract['symbol']}")
                print(f" self historical data counter = {self.historicalDataCounter} || iternal loop counter ={counter}")
                time.sleep(3)
            counter+=1
        #reset historical data counter for next use
        self.historicalDataCounter =-1

        #creating data frame dictionary with pandas : 
        #taking all the data stored in the trading app object 'self.data' and turn it into a pandas dataframe for later use 
        self.turn_historicalDataFrame_toPandas()
        
    def turn_historicalDataFrame_toPandas(self):
        tickers=self.historicalDataFrame.keys()
        data_frame_dict={}
        for ticker in tickers:
            data_frame_dict[ticker] = pd.DataFrame(self.historicalDataFrame[ticker])
            data_frame_dict[ticker].set_index("date",inplace=True)
        
        self.historicalDataFrame = data_frame_dict
            

############## RUN THE BOT ##################
if __name__ == "__main__":
    #INITAE TRADINGAPP
    AlgoP = TradingApp()
    time.sleep(5)
    #choose strategy
    current_strategy_name="strategy 1"
    backtets_mode=False
    #strat Algop
    AlgoP.play(current_strategy_name,backtets_mode)
 
