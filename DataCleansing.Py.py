import pandas as pd
import numpy as np
import os
import re
import sys

# Function to map sales brackets into numeric bins
def map_to_numeric(x):
    bracket1 = 114
    bracket2 = 123
    bracket3 = 125
    bracket4 = 131
    bracket5 = 132

    if (x == bracket1):
        return 50000
    elif (x == bracket2):
        return 175000
    elif (x == bracket3):
        return 375000
    elif (x == bracket4):
        return 750000
    elif (x == bracket5):
        return 1500000
    else:
        return 0

# Read in data using relative paths
ORIG_DATA_DIR = "original_data\\"
tax_data = pd.read_csv("12zpallagi.csv")
population = pd.read_excel("population.xlsx")

# Check command line argument
industry_type = None
if (len(sys.argv) <= 1):
    print("Please call this script with an industry parameter")
    exit()
elif (len(sys.argv) > 2):
    print("Incorrect number of arguments. Please enter industry parameter only")
else:
     industry_type = sys.argv[1]

# Start cleaning sales data
sales_data = pd.DataFrame()

# Combine sales data together
for data_file in os.listdir(ORIG_DATA_DIR):
    temp = pd.read_csv(ORIG_DATA_DIR + data_file)
    # Strip off header row and remove redundant columns
    temp = temp.iloc[1:, [1, 4, 5, 8]]
    sales_data = sales_data.append(temp)

# Rename columns
sales_data.columns = ["Zipcode",  "Industry",  "SalesId", "NumEstablishments"]

# Filter data for a particular industry
sales_data = sales_data[sales_data.Industry == industry_type]

# Typecast number strings into numeric dtype
sales_data.SalesId = pd.to_numeric(sales_data.SalesId)
sales_data.NumEstablishments = pd.to_numeric(sales_data.NumEstablishments)
sales_data.Zipcode = pd.to_numeric(sales_data.Zipcode)

# Estimate average revenue per establishment
sales_data["SalesIdVal"] = sales_data["SalesId"].apply(map_to_numeric)
sales_data["Sales"] = sales_data["SalesIdVal"] * sales_data["NumEstablishments"]
sales_data = sales_data[sales_data["Sales"] > 0]
sales_data = sales_data.groupby(["Zipcode"]).sum()
sales_data['AvgSales'] = sales_data['Sales'] / sales_data['NumEstablishments']

# Filter out invalid zipcodes
valid_zips = np.logical_and(tax_data.zipcode != 0, tax_data.zipcode != 99999)
tax_data = tax_data[valid_zips]


# Start cleaning tax data
tax_data = tax_data[['zipcode', 'AGI_STUB', 'N1', 'MARS1', 'MARS2', "NUMDEP",
 "SCHF", "N00200", "N01400", "N01700", "N02300", "N02500", "N03300"]]

cleaned_tax = []

for zip in pd.unique(tax_data.zipcode):
    subset = tax_data[tax_data.zipcode == zip]
    total_returns = sum(subset.N1)
    row = [zip, total_returns]

    # Get percent returns in each income bracket
    row.extend(subset.N1 / total_returns)

    # Aggregate columns and convert to percentages
    for col in subset.columns.values[3: ]:
        row.append(sum(subset[col]) / total_returns)

    cleaned_tax.append(row)

cleaned_tax_df = pd.DataFrame(cleaned_tax, columns = ["Zipcode", "TotalReturns", "Bracket1", "Bracket2", "Bracket3",
"Bracket4", "Bracket5", "Bracket6", "Single", "Married", "Dependent", "Farm", "Salaried",
"IndivRetirements", "TaxablePensions", "Unemployment", "SocialSecurity", "SelfEmployedRetirement"])


# Merge all data together
sales_tax_df = pd.merge(left = sales_data, right = cleaned_tax_df, left_on = "Zipcode", right_on = "Zipcode")

combined_df = pd.merge(left = sales_tax_df, right = population, left_on = "Zipcode", right_on = "Zip")
combined_df.to_csv("combined.csv")
