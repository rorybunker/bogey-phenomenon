#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined k-category (k=3) Wald-Wolfowitz Runs Test and Bogey player identification method using
data from professional men's tennis.
The original (k=2) Wald-Wolfowitz Runs Test portion of this code was 
adapted from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

k-Category Extension of the Single-Sample Runs Test for Randomness
https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/NCSS/Analysis_of_Runs.pdf
pages 256-6/256-7

The data, Data_Clean.csv, is the same dataset Angelini et al. (2022), which
had been passed through the clean() function in the authors' welo R package 

@author: rorybunker
"""

import pandas as pd
import math
import scipy.stats as st # for pvalue 
import numpy as np
import sys
pd.options.mode.chained_assignment = None
import warnings
warnings.filterwarnings("ignore")

def add_upset_type_column1(p1, p2, df_p1_p2):
    
    if 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1:
        return "UW"
    elif 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2:
        return "UL"
    else:
        return "N"
    
def add_upset_type_column2(p1, p2, df_p1_p2):
    if 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2:
        return "UW"
    elif 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1:
        return "UL"
    else:
        return "N"
  
def get_ur_list(p1, p2, df_p1_p2):
    df_p1_p2["upset_type_p1"] = df_p1_p2.apply(lambda x: add_upset_type_column1(p1, p2, x), axis = 1)
    df_p1_p2["upset_type_p2"] = df_p1_p2.apply(lambda x: add_upset_type_column2(p1, p2, x), axis = 1)
    
    ur_list = []
    for r in df_p1_p2["upset_type_p1"]:
        #if r != 'N':
        ur_list.append(r)
 
    return ur_list,  list(df_p1_p2['Date'])

def list_of_tuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

# Finds runs in data: counts and creates a list of them
def getRuns(L):
  import itertools
  return len([sum(1 for _ in r) for _, r in itertools.groupby(L)])

# define the WW runs test described above
def WW_runs_test(R, n1, n2, n):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((2*n1*n2) * (2*n1*n2 - n)) / ((n**2)*(n-1)) )

    # compute the expected value of R if the null is true
    muR = ((2*n1*n2)/n) + 1

    # test statistic: R vs muR
    z = (R - muR) / seR

    return z

def WW_runs_test_k_3(R, n1, n2, n3, n, z_type):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((n1**2 + n2**2 + n3**2)*((n1**2 + n2**2 + n3**2) + n*(n+1)) - 2*n*(n1**3 + n2**3 + n3**3) - n**3)/(n**2*(n - 1)) ) 
    # compute the expected value of R if the null is true
    muR = (n*(n+1) - (n1**2 + n2**2 + n3**2))/n
                   
    if z_type == "standard":
        # asymptotic standard normal z statistic
        z = (R - muR) / seR
    
    elif z_type == "cc":
        # asymptotic continuity-corrected standard normal z statistic
        if R >= muR: 
            z = (R - muR - 0.5)/seR
        elif R < muR:
            z = (R - muR + 0.5)/seR
            
    return z

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

def main():    
    df = pd.read_csv('https://raw.githubusercontent.com/rorybunker/bogey-teams-players-sport/main/Data_Clean.csv', low_memory=False)

    # ===================== SET PARAMETERS ===================== #
    p1 = 'Ferrer D.'
    p2 = 'Lopez F.'
    
    # uncomment if you want to run for a specific tournament
    # df = df[(df["Tournament"] == "Australian Open")]
    
    # uncomment if you want to run for Grand Slams only
    # df = df[(df["Series"] == "Grand Slam")]
    
    # uncomment if you want to run for *non* Grand Slams only
    # df = df[(df["Series"] != "Grand Slam")]
    
    # specify dates in format "YYYY-MM-DD" if you want to run for a specific date range
    # or use start_date = min(df["Date"]) and end_date = max(df["Date"]) for whole range
    start_date = min(df["Date"])
    end_date = max(df["Date"])
    # ========================================================== #
    
    df = df[((df["Date"] >= start_date) & (df["Date"] <= end_date))]
    
    # if AvgW or AvgL is null, replace with B365 odds
    df['AvgW'] = df['AvgW'].fillna(df['B365W'])
    df['AvgL'] = df['AvgL'].fillna(df['B365L'])
    
    df_p1_p2 = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1))]
    
    # match results for the given parameters
    RS = get_ur_list(p1, p2, df_p1_p2)[0]
    # corresponding match dates
    RS_date_list = get_ur_list(p1, p2, df_p1_p2)[1]
    
    # Gather info 
    numRuns = getRuns(RS) # Grab streaks in the data
    
    if numRuns == 1:
        print(pd.DataFrame.from_records(list_of_tuples(RS_date_list, RS), columns =['Date', 'Result']).to_string(index=False))
        sys.exit('Only 1 run so not possible to calculate Z in WWRT - bogey effect does not exist')
    
    RS_unique = unique(RS)
    
    r1 = []
    r2 = []
    r3 = []
    for r in RS:
        if r == RS_unique[0]:
            r1.append(r)
        elif r == RS_unique[1]:
            r2.append(r)
        elif r == RS_unique[2]:
            r3.append(r)
            
    R = numRuns      # number of runs
    n1 = len(r1)
    n2 = len(r2)
    n3 = len(r3)   
    n = n1 + n2 + n3

    # Run the WWRT
    # ww_z = WW_runs_test(R, n1, n2, n)
    ww_z_k_3 = WW_runs_test_k_3(R, n1, n2, n3, n, "cc")
    
    # calculate p-values
    p_values_one = st.norm.sf(abs(ww_z_k_3))   # one-sided
    p_values_two = st.norm.sf(abs(ww_z_k_3))*2 # two-sided
    
    # Print results
    print('==== RESULTS ====')
    print('Results set (RS):')
    print(pd.DataFrame.from_records(list_of_tuples(RS_date_list, RS), columns =['Date', 'Result']).to_string(index=False))
    print()     
    print('Wald-Wolfowitz Runs Test')
    print('Number of runs: %s' %(R))
    print('Number of Ns: %s; Number of ULs: %s; Number of UWs: %s ' %(n1,n2,n3))
    print('Z value: %s' %(ww_z_k_3))
    print('One tailed P value: %s; Two tailed P value: %s ' %(p_values_one, p_values_two))
    print()

if __name__ == '__main__':
    main()
