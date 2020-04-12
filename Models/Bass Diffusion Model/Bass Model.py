from scipy.optimize import leastsq
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np

# Based off NForouzandehmehr's implementation of the bass model on github
# Modelling for the Ford Hybrid Car's case on Decision Pro.Biz
# Deon Li
#------------------------------------------------------------------------

# residual (error) function
def residual(vars, t, sales, market_value, cumulative = False):
    P = vars[0]
    Q = vars[1]
    if (not cumulative):
        Bass = market_value * (((P+Q)**2/P)*np.exp(-(P+Q)*t))/(1+(Q/P)*np.exp(-(P+Q)*t))**2
    else:
        Bass = market_value * (1-np.exp(-(p+q) * t))/(1+(q/p)*np.exp(-(p+q) * t))
    return (Bass - (sales))

#time intervals
t= np.linspace(0.0, 8.0, num=9)
# Variable Market Potential
market_value = np.array([10, 10.11, 10.22, 10.33, 10.44, 10.56, 10.67, 10.79, 10.91, 11.03, 11.15, 11.27, 11.40, 11.52, 11.65, 11.78, 11.91])
# sales vector
sales=np.array([0.024350, 0.020287, 0.035, 0.047525, 0.088, 0.215, 0.252636, 0.35, 0.314271])
# cumulatice sales
c_sales=np.array([0.02435, 0.044637, 0.079637, 0.127162, 0.215162, 0.430162, 0.682798, 1.032792, 1.347069])
# initial variables(M, P & Q)
vars = [0.03,0.38]
                 
# non linear least square fitting
varfinal,success = leastsq(residual, vars, args=(t, sales, market_value[0:9], False))
print(success)

# estimated coefficients
p = varfinal[0]
q = varfinal[1]

#time interpolation
tp=(np.linspace(0.0, 16.0, num=17))
cofactor= np.exp(-(p+q) * tp)

print(varfinal)
#sales plot (pdf)
sales_pdf= market_value* (((p+q)**2/p)*cofactor)/(1+(q/p)*cofactor)**2
plt.plot(tp, sales_pdf,t,sales)
plt.title('Sales Over Time')
plt.legend(['Fit', 'True'])
plt.show()


# Cumulative sales (cdf)
sales_cdf= market_value*(1-cofactor)/(1+(q/p)*cofactor)
plt.plot(tp, sales_cdf,t,c_sales, tp, market_value)
plt.title('Cumulative Sales Over Time')
plt.legend(['Fit', 'True', 'Market Potential'])
plt.show()