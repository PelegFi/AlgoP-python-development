from indicators import Indicators
import Utilities
# print(Utilities.returns_percentage_to_decimal([10,29,-15,101,-99,6000,0,100,-1]))
precentage_returns=[0,0,0,-4]
returns_percentage_to_decimal=Utilities.returns_percentage_to_decimal(precentage_returns)
print(returns_percentage_to_decimal)
calculate_compound_returns=Utilities.calculate_compound_returns(precentage_returns)
print(calculate_compound_returns)
print(len(precentage_returns))
print(Utilities.CAGR(calculate_compound_returns,len(precentage_returns)))   