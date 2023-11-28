import pandas as pd

# Corrected data dictionary
data = {
    "col1": [1, "a"],
    "col2": [2, "b"],
    "col3": [3, "c"],
    "col4": [4, "d"]
}

# Create DataFrame with 'row1' and 'row2' as index labels
dataFrame = pd.DataFrame(data, index=["row1", "row2"])
print(dataFrame)
# Append a new row to the DataFrame
# This row must have the same columns as the existing DataFrame
dataFrame = dataFrame._append(pd.DataFrame({"col1": ["added_value"], 
                                           "col2": ["added_value"],
                                           "col3": ["added_value"],
                                           "col4": ["added_value"]}, 
                                          index=["added row"]))

print(dataFrame)
