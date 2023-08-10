#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined Wald-Wolfowitz Runs Test and Bogey player identification method using
data frmo professional men's tennis.
The Wald-Wolfowitz Runs Test portion of this code was 
adapted from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

The data, Data_Clean.csv, is the same dataset Angelini et al. (2022), which
had been passed through the clean() function in the authors' welo R package 
@author: rorybunker
"""
import itertools
import pandas as pd
import math
import scipy.stats as st # for pvalue 
import numpy as np
import sys
import argparse
pd.options.mode.chained_assignment = None
import warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-p1', '--player_1', type=str, required=False, default='all', help='player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)')
parser.add_argument('-p2', '--player_2', type=str, required=False, default='all', help='player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)')
parser.add_argument('-d', '--dataset', type=str, required=True, help='atp (mens) or wta (womens) or test')
parser.add_argument('-g', '--grand_slam', type=int, required=False, default=2, help='0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)')
parser.add_argument('-t', '--tournament', type=str, required=False, default='all', help='tournament name, e.g., Australian Open')
parser.add_argument('-s', '--s_date', type=str, required=False, default='min', help='start date in YYYY-MM-DD format (default = min date in dataset)')
parser.add_argument('-e', '--e_date', type=str, required=False, default='max', help='end date in YYYY-MM-DD format (default = max date in dataset)')
parser.add_argument('-z', '--z_val_type', type=str, required=False, default='cc', help='type of z statistic - standard std or continuity corrected cc (default = cc)')
parser.add_argument('-p', '--p_adj_method', type=str, required=False, default='BH', help='p-value adjustment for multiple comparisons method, e.g., bonferroni, hochberg, BH, holm, hommel, BY')
parser.add_argument('-alpha', '--sig_level', type=float, required=False, default=0.05, help='level of statistical significance, alpha. Default is alpha = 0.05')
args, _ = parser.parse_known_args()

# create historical result set, HR, which consists of upset results, U, and non-upset results, N.
def check_hr_set(p1, p2, df_p1_p2):
    if (1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1) or (1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2):
        return "U"
    else:
        return "N"
    
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
  
def get_hr_list(p1, p2, df_p1_p2):
    df_p1_p2["hr_check"] = df_p1_p2.apply(lambda x: check_hr_set(p1, p2, x), axis = 1)
    #hr_list = []
    
    #for val in df_p1_p2["hr_check"]:
    #    hr_list.append(val)
    
    return list(df_p1_p2['hr_check']), list(df_p1_p2['Date'])

def get_ur_list(p1, p2, df_p1_p2):
    df_p1_p2["upset_type_p1"] = df_p1_p2.apply(lambda x: add_upset_type_column1(p1, p2, x), axis = 1)
    df_p1_p2["upset_type_p2"] = df_p1_p2.apply(lambda x: add_upset_type_column2(p1, p2, x), axis = 1)
    
    ur_list = []
    for r in df_p1_p2["upset_type_p1"]:
        if r != 'N':
            ur_list.append(r)
 
    return ur_list,  list(df_p1_p2['Date'])

def list_of_tuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

# Finds runs in data: counts and creates a list of them
def getRuns(L):
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

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

def main(): 
    if args.dataset == 'test':
        df = pd.read_csv('Data_Clean_Test.csv', low_memory=False)
    elif args.dataset == 'wta':
        df = pd.read_csv('Data_Clean_WTA.csv', low_memory=False)
    elif args.dataset == 'atp':
        df = pd.read_csv('Data_Clean.csv', low_memory=False)

    if args.tournament != 'all':
        df = df[(df["Tournament"] == args.tournament)]

    if args.grand_slam == 0:
        df = df[(df["Series"] != "Grand Slam")]
    elif args.grand_slam == 1:
        df = df[(df["Series"] == "Grand Slam")]

    if args.s_date == 'min':
        start_date = min(df["Date"])
    elif args.s_date != 'min':
        start_date = args.s_date

    if args.e_date == 'max':
        end_date = max(df["Date"])
    elif args.e_date != 'max':
        end_date = args.e_date
    
    p1 = args.player_1
    p2 = args.player_2
    
    df = df[((df["Date"] >= start_date) & (df["Date"] <= end_date))]
    
    # if AvgW or AvgL is null, replace with B365 odds
    df['AvgW'] = df['AvgW'].fillna(df['B365W'])
    df['AvgL'] = df['AvgL'].fillna(df['B365L'])
    
    df_p1_p2 = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1))]
    
    # match results for the given parameters
    HR, HR_date_list = get_hr_list(p1, p2, df_p1_p2)
    
    # Gather info 
    numRuns = getRuns(HR) # Grab streaks in the data
    
    if numRuns == 1:
        print(pd.DataFrame.from_records(list_of_tuples(HR_date_list, HR), columns =['Date', 'Result']).to_string(index=False))
        sys.exit('Only 1 run so not possible to calculate Z in WWRT - bogey effect does not exist')
    
    HR_unique = unique(HR)
    
    u1 = []
    u2 = []
    for u in HR:
        if u == HR_unique[0]:
            u1.append(u)
        elif u == HR_unique[1]:
            u2.append(u)
    
    # Define parameters
    R = numRuns      # number of runs
    n1 = len(u1)     # number of 'NOT UPSET'
    n2 = len(u2)     # number of 'UPSET NOT WIN'
    n = n1 + n2      # should equal len(L)

    # Run the WWRT
    ww_z = WW_runs_test(R, n1, n2, n)
    
    # calculate p-values
    p_values_one = st.norm.sf(abs(ww_z))   # one-sided
    p_values_two = st.norm.sf(abs(ww_z))*2 # two-sided
    
    # Print results
    print(str(p1) + " vs. " + str(p2))
    print('==== STEP 1 RESULTS ====')
    print('Historical results set (HR):')
    print(pd.DataFrame.from_records(list_of_tuples(HR_date_list, HR), columns =['Date', 'Result']).to_string(index=False))
    print()     
    print('Wald-Wolfowitz Runs Test')
    print('Number of runs: %s' %(R))
    print('Number of Ns: %s; Number of Us: %s ' %(n1,n2))
    print('Z value: %s' %(ww_z))
    print('One tailed P value: %s; Two tailed P value: %s ' %(p_values_one, p_values_two))
    print()
    
    # === STEP 2 === #
    # if 1-sided p-value is statistically significant continue
    if p_values_one < args.sig_level:
        UR = get_ur_list(p1, p2, df_p1_p2)[0]
        UR_date_list = get_ur_list(p1, p2, df_p1_p2)[1]
        
        print('==== STEP 2 RESULTS ====')
        print('Upset results set (UR):')
        print(pd.DataFrame.from_records(list_of_tuples(UR_date_list, UR), columns =['Date', 'Result']).to_string(index=False))
        print()
        
        ul_count = 0
        uw_count = 0
        
        for r in UR:
            if r == 'UW':
                uw_count += 1
            elif r == 'UL':
                ul_count += 1
        
        UR_unique = unique(UR)
        numRuns = getRuns(UR)
        
        u1 = []
        u2 = []
        for u in UR:
            if u == UR_unique[0]:
                u1.append(u)
            elif u == UR_unique[1]:
                u2.append(u)
    
        # Define parameters
        R = numRuns      # number of runs
        n1 = len(u1)     # number of 'NOT UPSET'
        n2 = len(u2)     # number of 'UPSET NOT WIN'
        n = n1 + n2      # should equal len(L)
    
        # Run the WWRT
        if numRuns > 1:
            ww_z = WW_runs_test(R, n1, n2, n)     
            p_values_one = st.norm.sf(abs(ww_z))
            print('p-value for WWRT on UR: ' + str(p_values_one))
            
        print('Number of UWs: %s' %(uw_count))
        print('Number of ULs: %s' %(ul_count))
        print(str(uw_count/(uw_count + ul_count)*100) + '% of upset results were UWs')
        print(str(ul_count/(uw_count + ul_count)*100) + '% of upset results were ULs')
        print(str(uw_count/len(df_p1_p2)*100) + '% of matches were UWs')
        print(str(ul_count/len(df_p1_p2)*100) + '% of matches were ULs')
        
if __name__ == '__main__':
    main()
