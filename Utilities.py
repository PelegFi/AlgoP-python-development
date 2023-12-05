from ibapi.contract import Contract
from ibapi.order import Order
import numpy as np
import math
import time
import scipy.stats
import TradingApp
import datetime

class Utilities ():
    ############################## ORDERS  ######################################
    def place_order(tradingApp:TradingApp , contract:Contract , order : Order):
        tradingApp.reqIds(-1)
        time.sleep(1)
        orderId = tradingApp.nextValidOrderId
        tradingApp.placeOrder(orderId,contract,order)

    def market_order(action, quantity):
        order = Order()
        order.action = action  # 'BUY' or 'SELL'
        order.orderType = "MKT"  # Market order
        order.totalQuantity = quantity

        #i dont know why the fuck i need this shit but its essential 
        order.eTradeOnly = False
        order.firmQuoteOnly = False

        return order

    def limit_order(action, quantity, price):
        order = Order()
        order.action = action  # 'BUY' or 'SELL'
        order.orderType = "LMT"  # Limit order
        order.totalQuantity = quantity
        order.lmtPrice = price

        #i dont know why the fuck i need this shit but its essential 
        order.eTradeOnly = False
        order.firmQuoteOnly = False

        return order

    def stop_order(action, quantity, stop_price):
        order = Order()
        order.action = action  # 'BUY' or 'SELL'
        order.orderType = "STP"  # Stop order
        order.totalQuantity = quantity
        order.auxPrice = stop_price  # Stop price

        #i dont know why the fuck i need this shit but its essential 
        order.eTradeOnly = False
        order.firmQuoteOnly = False

        return order

    def trailing_stop_order(action,quantity,trailing_stop_price,trailing_percent):
        order = Order()
        order.action = action  # 'BUY' or 'SELL'
        order.orderType = "TRAIL"  # Trailing stop order
        order.totalQuantity = quantity
        order.trailingPercent = trailing_percent  # Trailing stop percentage
        order.auxPrice = trailing_stop_price  # Trailing stop price

        #i dont know why the fuck i need this shit but its essential 
        order.eTradeOnly = False
        order.firmQuoteOnly = False

        return order
    ############################## OTHER UTILITIES ######################################
    def createContract(symbol: str, secType: str, currency: str, exchange: str, LastTradeDateOrContractMonth: str = None) -> Contract:
        # Create a new Contract object
        contract = Contract()
        
        # Set the attributes of the contract
        contract.symbol = symbol
        contract.secType = secType
        contract.currency = currency
        contract.exchange = exchange
        
        # Set the lastTradeDateOrContractMonth based on the provided argument -> relevant only for CFD + FUT 
        if LastTradeDateOrContractMonth is not None:
            contract.lastTradeDateOrContractMonth = LastTradeDateOrContractMonth
        
        return contract

    def returns_percentage_to_decimal(precntage_returns:list):
        decimal_returns=[]
        for current_return in precntage_returns:
            if  current_return < -100 :
                print(f"INVALID RETURN : {current_return}")
                break
            elif current_return > 0 :
                decimal_returns.append((current_return/100)+1)
            elif current_return < 0 :
                if current_return != -100:
                    decimal_returns.append(1 - abs(current_return) / 100)
                else : 
                    print("turn_precentage_to_decimal -> ERROR : YOU HAVE LOST 100%")
                    break
            elif current_return == 0 :
                decimal_returns.append(0)
        
        return decimal_returns

    def calculate_compound_returns(percentage_returns:list):
        decimal_returns =Utilities.returns_percentage_to_decimal(percentage_returns)

        compound_sum = 1
        for current_return in decimal_returns:
            if current_return !=0:
                compound_sum *= current_return

        return (compound_sum -1 ) * 100

    def sharpe_ratio_annualize(CAGR,yearly_risk_free_rate,volatility)->float:
        return ((CAGR-yearly_risk_free_rate)/(volatility))

    def volatility(returns:np.array):
        return returns.std()    
        
    def CAGR(compound_return:float,years:int):
        """
        Calculate the Compound Annual Growth Rate (CAGR) based on the compound return and the number of years.

        Parameters:
        - compound_return (float): The compound return as a percentage.
        - years (int): The number of years over which the CAGR is calculated.

        Returns:
        - float: The Compound Annual Growth Rate (CAGR) as a percentage.

        Formula:
        CAGR = (((compound_return + 100) / 100) ** (1 / years) - 1) * 100

        The CAGR is a measure of the geometric progression ratio that provides a constant rate of return over a specified time period. It is commonly used to evaluate and compare the past performance of investments.
        """
        return (((((compound_return+100)/100))**(1/years)-1)*100)
        
    def hypothesisTesting(returns:np.array,alpha_level:float=0.01)->bool:
        """
        Conducts a hypothesis test on the average returns of a given dataset.

        Parameters:
        - returns (numpy.array): An array containing the returns data for the hypothesis test.

        Returns:
        - bool: Returns True if the null hypothesis is rejected at a significance level of 0.01,
                indicating a statistically significant difference in average returns.
                Returns False otherwise.

        Methodology:
        1. Null Hypothesis (H0): The average returns are equal to zero.
        2. Alternative Hypothesis (H1): The average returns are not equal to zero.
        3. Calculates the standard test statistic using the provided returns data, assuming
        a normal distribution under the null hypothesis.
        4. Calculates the p-value associated with the test statistic.
        5. If the p-value is less than or equal to 0.01, the null hypothesis is rejected,
        indicating a statistically significant difference in average returns.

        Note: The method utilizes scipy.stats for statistical calculations.
        """
        
        H0_retruns_avg=0
        H0_retruns_std=returns.std()
        H1_returns_avg=returns.mean()

        #calculating standart_test_statistics using H0 hypothesis avg and std
        standart_test_statistics=(H1_returns_avg-H0_retruns_avg/H0_retruns_std)*math.sqrt(H1_returns_avg.len())

        #calculating p-value
        p_value=scipy.stats.norm.sf(abs(standart_test_statistics))
        if p_value<=alpha_level:
            return True
        elif p_value>alpha_level:
            return False
        
    def calculate_profit_percentage(start_price, end_price, trade_action):
        percentage = 0.0
        pnl = 0.0

        if trade_action == "BUY":
            if start_price < end_price:
                pnl = end_price - start_price
                percentage = (pnl / start_price) * 100
            elif start_price > end_price:
                pnl = start_price - end_price
                percentage = -((pnl / start_price) * 100)

        elif trade_action == "SELL":
            if start_price > end_price:
                pnl = start_price - end_price
                percentage = (pnl / start_price) * 100
            elif start_price < end_price:
                pnl = end_price - start_price
                percentage = -((pnl / start_price) * 100)

        elif trade_action not in ["BUY", "SELL"]:
            # Invalid trade action, return NaN to indicate an error.
            percentage = float('nan')

        return percentage

    def print_backtest_result(result: dict):
        for ticker in result:
            metric_dict = result[ticker]
            print(f"--- SHOWING RESULT FOR TICKER {ticker} -----")
            print(f"-> RETURNS : {metric_dict['returns']} || \n SUM = {sum(metric_dict["returns"])}")
            print(f"-> trade_count : {metric_dict['trade_count']}")
            print(f"-> compound_returns : {metric_dict['compound_returns']}")
            print(f"-> volatility : {metric_dict['volatility']}")

            # Check if 'CAGR' and 'SHARPE_ANNUAL' are in the results for the ticker
            if "CAGR" in metric_dict:
                print(f"-> CAGR : {metric_dict['CAGR']}")
            if "SHARPE_ANNUAL" in metric_dict:
                print(f"-> SHARPE_ANNUAL : {metric_dict['SHARPE_ANNUAL']}")
            
            print("\n")  # Add a newline for better separation between tickers

    def calc_backtest_min_time():
        return "10 D"

    def time_in_loop(candles_time_frame, current_loop_start_time):
        #candles time frame should be in inteactive brokers format 
        #loop_start_time need to be in seconds
        parts = candles_time_frame.split(" ")  # Split timeframe string on space
        amount_of_time_frame = int(parts[0])
        time_frame = parts[1]

        current_time = time.time()  # Current time in seconds
        elapsed_time = current_time - current_loop_start_time

        if time_frame == "secs":
            return elapsed_time < amount_of_time_frame
        elif time_frame in ["min", "mins"]:
            return elapsed_time < amount_of_time_frame * 60
        elif time_frame in ["hour", "hours"]:
            return elapsed_time < amount_of_time_frame * 60 * 60
        elif time_frame == "day":
            return elapsed_time < amount_of_time_frame * 24 * 60 * 60
        elif time_frame == "week":
            return elapsed_time < amount_of_time_frame * 7 * 24 * 60 * 60
        elif time_frame == "month":
            # Approximate a month as 30 days
            return elapsed_time < amount_of_time_frame * 30 * 24 * 60 * 60

        print("error in function time_in_loop")
        return False

    def fromat_dateTime(time) -> str:
        dt_object = datetime.datetime.fromtimestamp(time)
        formatted_time = dt_object.strftime("%Y%m%d %H:%M:%S")
        return formatted_time