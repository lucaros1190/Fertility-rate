
# fitfert.py Python script to fit data with the function introduced by Ryan et al. (2016)
# Created by Luca Rossini on 27 December 2021
# E-mail luca.rossini@unitus.it
# Last update 21 January 2022

import pandas as pd
import plotly.graph_objs as go
from math import *
from scipy import stats
from scipy.optimize import curve_fit
from scipy.stats.distributions import chi2
from scipy import odr
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

# Read the data to fit and plot

Data = pd.read_csv("data.txt", sep="\t", header=None)

# Set the header of the dataset

Data.columns = ["x", "y", "err_x", "err_y"]

x = Data['x']
y = Data['y']
err_x = Data['err_x']
err_y = Data['err_y']

# Fit data with the Ryan et al. function
    # Definition of the Ryan et al. function
    
def polifun(x, a, b, c, d, e):
    return a * ( ((b + 1) / (np.pi * (c ** (2 * b + 2)))) * ((c ** 2) - ( ((x - e) ** 2) + (d ** 2)) ) ** b )

    # Fit with curve_fit
    
popt, pcov = curve_fit(polifun, x, y, bounds=([90., 10., 20., 4., 19.], [75000., 900., 600., 90., 35.]), p0=(74000., 70., 50., 6., 23.))#, method='dogbox')

    # Best fit values
    
a = popt[0]
b = popt[1]
c = popt[2]
d = popt[3]
e = popt[4]

    # Perameters error

perr = np.sqrt(np.diag(pcov))

err_a = perr[0]
err_b = perr[1]
err_c = perr[2]
err_d = perr[3]
err_e = perr[4]


# Ask how many sigma do you want to include in the confidence band

print('\n How many sigma do you want to include in the confidence band? (2 sigma is 95%): \n')

num_sigma = float(input())

# Upper ad lower confidence bands

    # Create the linespace to plot the best fit curve

x_fun = np.linspace(0, 45, 1000)

    # Calculations

fitted_fun = polifun(x, *popt)
fitted_plot = polifun(x_fun, *popt)

a_up = a + num_sigma * err_a
a_low = a - num_sigma * err_a
b_up = b + num_sigma * err_b
b_low = b - num_sigma * err_b
c_up = c + num_sigma * err_c
c_low = c - num_sigma * err_c
d_up = d + num_sigma * err_d
d_low = d - num_sigma * err_d
e_up = e + num_sigma * err_e
e_low = e - num_sigma * err_e

upper_fit = polifun(x_fun, a_up, b_up, c_up, d_up, e_up)
lower_fit = polifun(x_fun, a_low, b_low, c_low, d_low, e_low)

# Calculating R-squared

resid = y - fitted_fun
ss_res = np.sum(resid**2)
ss_tot = np.sum((y - np.mean(y))**2)
r_squared = 1 - (ss_res / ss_tot)

# Number of degrees of freedom (NDF)

ndf = len(x) - 5

# Calculate the chi-squared (with error below the fraction)

chi_sq = 0
for i in range(len(x)):
    chi_sq = pow((y[i] - fitted_fun[i]), 2)/err_y[i]

# Calculate the P-value from chi-square

Pvalue = 1 - chi2.sf(chi_sq, ndf)

# Calculate AIC and BIC

AIC = 2 * 5 - 2 * np.log(ss_res/len(x))
BIC = 5 * np.log(len(x)) - 2 * np.log(ss_res/len(x))

# Print the results

print('\n Gamma fit results: \n')

    # Define the parameters' name

parname = (' a = ', ' b = ', ' c = ', ' d = ', ' e = ')

for i in range(len(popt)):
    print(parname[i] + str(round(popt[i], 7)) + ' +/- ' + str(round(perr[i],7)))

print(' R-squared = ', round(r_squared, 5))
print(' Chi-squared = ', round(chi_sq, 5))
print(' P-value = ', round(Pvalue, 7))
print(' Number of degrees of freedom (NDF) =', ndf)
print(' Akaike Information Criterion (AIC):', round(AIC, 5))
print(' Bayesian Information Criterion (BIC)', round(BIC, 5))
print('\n')

print(' Covariance matrix: \n')

    # Define the row names to print

rowname = (' ', 'a ', 'b ', 'c ', 'd ', 'e ')
print(rowname[0] + '  \t' + rowname[1] + '  \t\t' + rowname[2]+ '  \t\t' + rowname[3] +  '  \t\t' + rowname[4])

for i in range(len(pcov)):
    print(rowname[i+1] + ' ' + str(pcov[i]))

print(' ')

# Plot the data

plt.figure(1)

plt.scatter(x, y, color="C0", label=f"Experimental data")
plt.errorbar(x, y, xerr=err_x, yerr=err_y, fmt='o')
plt.plot(x_fun, fitted_plot, color="C1", label=f"Best fit function")
plt.fill_between(x_fun, upper_fit, lower_fit, color='b', alpha=0.1)
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()

plt.show()
