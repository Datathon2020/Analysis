import pandas as pd
import numpy as np
import os
import re

ORIG_DATA_DIR = "C:\\Python_Projects\\Datathon 2020\\original_data\\"
#ZIPCODE_DATA_DIR = "C:\\Python_Projects\\Datathon 2020\\zipcode_data\\"

# Merges original data (excluding metadata)
sales_data = pd.DataFrame()

for data_file in os.listdir(ORIG_DATA_DIR):
    temp = pd.read_csv(ORIG_DATA_DIR + data_file)
    # Strip off header row and remove redundant columns
    temp = temp.iloc[1:, [1, 4, 6, 8]]
    sales_data = sales_data.append(temp)


# Rename columns
sales_data.columns = ["Zipcode",  "Industry",  "SalesInfo", "NumEstablishments"]

# Typecast number strings into numeric dtype
sales_data.NumEstablishments = pd.to_numeric(sales_data.NumEstablishments)
sales_data.Zipcode = pd.to_numeric(sales_data.Zipcode)
