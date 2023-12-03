import openpyxl
from config_strategys import all_vars
from excels import Excels

path = all_vars["strategy 1"]["other_variables"]["excle_path_backtest"]

Excels.create_backtest_strategy1_excel(path)