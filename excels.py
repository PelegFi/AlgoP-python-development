import openpyxl
import time , datetime
from config_strategys import all_vars

class Excels():
    def __init__(self,path) -> None:
        current_dateTime = datetime.datetime.now()

        self.wb_path=path+"\\"+str(current_dateTime.strftime('%Y.%m.%d_%H-%M-%S'))+".xlsx"
        self.wb =openpyxl.Workbook()
        self.current_ws = self.wb.active

    def create_backtest_strategy1_excel(self):
        #setting up initial data table cells
        self.current_ws["A1"] = "Date"
        self.current_ws["B1"] = "Price"
        self.current_ws["C1"] = "Action"
        self.current_ws["D1"] = "Signal"
        self.current_ws["E1"] = "Zscore"
        self.current_ws["F1"] = "emaZ"
        self.current_ws["G1"] = "real p&l"
        self.current_ws["H1"] = "compound p&l"

        #saving
        self.wb.save(self.wb_path)
    
    def write_line_backtest_strategy1(self,date,price,action,signal,zscore,emaz,realPnL,compoundPnL):
        current_row=self.current_ws.max_row+1

        self.current_ws[f"A{current_row}"] = date
        self.current_ws[f"B{current_row}"] = price
        self.current_ws[f"C{current_row}"] = action
        self.current_ws[f"D{current_row}"] = signal
        self.current_ws[f"E{current_row}"] = zscore
        self.current_ws[f"F{current_row}"] = emaz
        self.current_ws[f"G{current_row}"] = realPnL
        self.current_ws[f"H{current_row}"] = compoundPnL

        #saving
        self.wb.save(self.wb_path)

if __name__ == "__main__" :
    path = all_vars["strategy 1"]["other_variables"]["excle_path_backtest"]
    print(path)
    new_excle = Excels(path)
    new_excle.create_backtest_strategy1_excel()