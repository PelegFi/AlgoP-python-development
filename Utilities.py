from ibapi.contract import Contract
from ibapi.order import Order
import numpy as np
import math
import scipy.stats


############################## ORDERS  ######################################
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
    decimal_returns =returns_percentage_to_decimal(percentage_returns)

    compound_sum = 1
    for current_return in decimal_returns:
        if current_return !=0:
            compound_sum *= current_return

    return (compound_sum -1 ) * 100

def sharpe_ratio(returns,risk_free_rate)->float:
        """
        Calculates the Sharpe ratio of a portfolio.

        Args:
            returns (np.ndarray): The returns of the portfolio.
            risk_free_rate (float): The risk-free rate of return.

        Returns:
            float: The Sharpe ratio of the portfolio.
        """

        excess_returns = returns - risk_free_rate
        sharpe_ratio = (np.mean(excess_returns) / np.std(excess_returns))
        return sharpe_ratio
    
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
    