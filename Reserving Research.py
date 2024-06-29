import pandas as pd
import chainladder as cl
import numpy as np

# Reading in the data
dat = pd.read_csv("Transaction Data.csv")

# Data set variables
# Finding the start origin year 
start_year = int(min(dat["OriginDate"].str.slice(start = -4)))
print("Start year is: ", start_year)

# Finding the accident year for each claim
dat["AccidentYear"] = dat["OriginDate"].str.slice(start = -4)
dat['AccidentYear'] = dat['AccidentYear'].astype(int)

# Finding the year of transaction for each transaction
dat["TransactionYear"] = dat["TransactionDate"].str.slice(start = -4)
dat['TransactionYear'] = dat['TransactionYear'].astype(int)

# Converting the data to triangle format - all the data is used
initial = cl.Triangle(
    dat, 
    origin = "AccidentYear",
    origin_format = "%d-%m-%Y",    
    development = "TransactionYear",
    development_format = "%d-%m-%Y",
    columns = "IncurredMvt",
    cumulative = False
)

# Converting the triangle from incremental to cumulative
initial = initial.incr_to_cum()
print(initial)

# Finding the link ratios
print(initial.link_ratio)

# The valuation date
print(initial.valuation_date)

# ---------------------------------------------------------------------------------------------------------------------------------

# Setting the valuation date 
val_year = 2018

# Subsetting the claims data to claims that occurred before the valuation date
print(dat)
val_dat = dat[dat["TransactionYear"] < (val_year + 1)]

val_triangle = cl.Triangle(
    val_dat,
    origin = "AccidentYear",
    origin_format = "%d-%m-%Y",    
    development = "TransactionYear",
    development_format = "%d-%m-%Y",
    columns = "IncurredMvt",
    cumulative = False
)

# Changes the triangle from incremental to cumulative 
val_triangle = val_triangle.incr_to_cum()

# The cumulative incurred claims triangle as at valuation date
print(val_triangle)

# Check: the valuation date of the triangle
print(val_triangle.valuation_date)

# The full triangle after applying the chain ladder
val_triangle_model = cl.Chainladder().fit(val_triangle)
print(val_triangle_model.full_triangle_)

# The predicted ultimate values for each origin year 
predicted_ultimate = val_triangle_model.ultimate_
predicted_ultimate = predicted_ultimate.to_frame()
print(predicted_ultimate)
#print(val_triangle_model.to_frame()) - AttributeError: 'Chainladder' object has no attribute 'to_frame'
#print("The type is: ", type(val_triangle_model)) - <class 'chainladder.methods.chainladder.Chainladder'>

# Finding the observed ultimate corresponding to the same period as the predicted ultimate
initial_triangle_dat = initial.to_frame()
observed_ultimate = initial_triangle_dat.iloc[0:(val_year - start_year + 1), (val_year - start_year)] 
print("These are the observed ultimates:","\n", observed_ultimate)

# Comparing the predicted ultimate values with the observed ultimate values for each origin year where ultimate is @ valuation date
predicted_ultimate = predicted_ultimate.rename(columns={'2261': 'Predicted'})
predicted_ultimate["Observed"] = observed_ultimate
ultimate = predicted_ultimate
print(ultimate)

# Ratio of predicted ultimate to observed ultimate 
print((ultimate["Predicted"]/ultimate["Observed"]))
