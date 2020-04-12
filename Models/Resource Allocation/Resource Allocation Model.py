from scipy.optimize import leastsq
from scipy.optimize import curve_fit
from scipy.optimize import LinearConstraint
from scipy.optimize import Bounds
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# change these:
base_data = pd.read_csv(r"Resource Allocation\Resource Allocation Base.csv", header = 0, index_col = 0)
effort_data = pd.read_csv(r"Resource Allocation\Resource Allocation Effort.csv", header = 0, index_col = 0)
impact_data = pd.read_csv(r"Resource Allocation\Resource Allocation Impact.csv", header = 0, index_col = 0)
base_data.sort_index(inplace=True)
effort_data.sort_index(inplace=True)
impact_data.sort_index(inplace=True)

# 14 Reigions, at most 52 in total, no negative

# Constraint 0 < x1 + x2 ... x14 < 52
linearConstraint = LinearConstraint([1 for i in range(0, base_data.shape[0])],[0], [base_data["Effort"].sum()])
# Constraint 0 < xi < 52 for i in range(0, number of areas)
bounds = Bounds([0 for i in range(0, base_data.shape[0])], [base_data["Effort"].sum() for i in range(0, base_data.shape[0])])
base_effort = base_data["Effort"]
margin = base_data["Margin"]
cost = base_data["Cost per Effort"]
order = base_data.index

vars = [10, 10]
vars_final = [(i, i) for i in range (0, len(order))]

# allocation function to optimize
def residual(vars, effort, sales):
    c = vars[0]
    d = vars[1]
    maximum = sales[-1]
    minimum = sales[0]
    predicted = minimum + (maximum - minimum)*((effort**c)/(d + (effort**c)))
    return (predicted - (sales))

def allocation_func(vars, maximum, minimum, effort):
    c = vars[0]
    d = vars[1]
    return minimum + (maximum - minimum)*((effort**c)/(d + (effort**c)))

def profit(effort, func_coef, sales, margin, cost, order):
    profit_amount = 0
    for count, segment in enumerate(order):
        cur_sales = sales.loc[segment]
        profit_amount += margin.loc[segment]*(allocation_func(func_coef[count], cur_sales[-1], cur_sales[0], effort[count])) - cost.loc[segment]*effort[count]
    return -1*profit_amount

def individual_profit(effort, func_coef, maximum, minimum, margin, cost):
    return margin*allocation_func(func_coef, maximum, minimum, effort) - cost*effort

effort_series = (np.linspace(0.0, 16.0, num=17))
# Determine C/D in the allocation function
for count, segment in enumerate(order):
    vars_final[count], success = leastsq(residual, vars, args=(effort_data.loc[segment], impact_data.loc[segment]))
    # sales_pdf = allocation_func(vars_final[count], impact_data.loc[segment][-1], impact_data.loc[segment][0], effort_series)
    # plt.scatter(effort_data.loc[segment][0:-1], impact_data.loc[segment][0:-1])
    # plt.plot(effort_series, sales_pdf)
    # plt.title('Effort to Sales, ' + segment)
    # plt.show()

base_data["Maximum"] = impact_data.max(axis=1)
base_data["Minimum"] = impact_data.min(axis=1)
base_data.insert(loc=len(base_data.columns),column="c", value=[variable[0] for variable in vars_final], allow_duplicates=True)
base_data.insert(loc=len(base_data.columns),column="d", value=[variable[1] for variable in vars_final], allow_duplicates=True)
base_data["Profit"] = base_data.apply(lambda row: row["Margin"]*row["Sales"] - row["Effort"]*row["Cost per Effort"], axis=1)
effort_values = minimize(profit, base_effort.tolist(), args=(vars_final, impact_data, margin, cost, order), method="trust-constr", constraints=linearConstraint, bounds=bounds)
base_data["Optimized Effort"] = effort_values.x.round(2)
base_data["Optimized Profit"] = base_data.apply(lambda row: individual_profit(row["Optimized Effort"], (row["c"], row["d"]), row["Maximum"], row["Minimum"], row["Margin"], row["Cost per Effort"]), axis = 1)

# Output
results_df = pd.DataFrame({"Base Effort":base_effort, "Optimized Effort":effort_values.x.round(2), "Base Profit": base_data["Profit"].round(2), "Optimized Profit": base_data["Optimized Profit"].round(2)}, index = order)
results_df[r"% Effort"] = 100*((results_df["Optimized Effort"] - results_df["Base Effort"])/results_df["Base Effort"]).round(2)
results_df[r"% Profit"] = 100*((results_df["Optimized Profit"] - results_df["Base Profit"])/results_df["Base Profit"]).round(2)

print("\nHere are the optimal effort results: \n", results_df)
print("Current Profit is: ", round(results_df["Base Profit"].sum()))
print("Total Optimized Profit is: ", round(results_df["Optimized Profit"].sum()))

