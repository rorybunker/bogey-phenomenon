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

import csv
import pandas as pd
import math
import scipy.stats as st # for pvalue
import numpy as np
import warnings
import argparse

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--player_1', type=str, required=False, default='all', help='player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)')
parser.add_argument('-b', '--player_2', type=str, required=False, default='all', help='player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)')
parser.add_argument('-d', '--dataset', type=str, required=True, help='atp (mens) or wta (womens) or test')
parser.add_argument('-g', '--grand_slam', type=int, required=False, default=2, help='0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)')
parser.add_argument('-t', '--tournament', type=str, required=False, default='all', help='tournament name, e.g., Australian Open')
parser.add_argument('-s', '--s_date', type=str, required=False, default='min', help='start date in YYYY-MM-DD format (default = min date in dataset)')
parser.add_argument('-e', '--e_date', type=str, required=False, default='max', help='end date in YYYY-MM-DD format (default = max date in dataset)')
parser.add_argument('-z', '--z_val_type', type=str, required=False, default='cc', help='type of z statistic - standard std or continuity corrected cc (default = cc)')
parser.add_argument('-p', '--p_adj_method', type=str, required=False, default='BH', help='p-value adjustment for multiple comparisons method, e.g., bonferroni, hochberg, BH, holm, hommel, BY')
args, _ = parser.parse_known_args()

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

def WW_runs_test_k_3(R, n1, n2, n3, n, z_type):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((n1**2 + n2**2 + n3**2)*((n1**2 + n2**2 + n3**2) + n*(n+1)) - 2*n*(n1**3 + n2**3 + n3**3) - n**3)/(n**2*(n - 1)) )
    # compute the expected value of R if the null is true
    muR = (n*(n+1) - (n1**2 + n2**2 + n3**2))/n

    if seR == 0:
        return 0

    if z_type == "std":
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

def adjust_pvalues(p_val_csv, p_adj_method):
    from rpy2.robjects.packages import importr
    from rpy2.robjects.vectors import FloatVector

    stats = importr('stats')

    p_val_1_list = p_val_csv['p_val_1'].tolist()
    p_val_2_list = p_val_csv['p_val_2'].tolist()

    p_val_1_adjusted = stats.p_adjust(FloatVector(p_val_1_list), method=p_adj_method)
    p_val_2_adjusted = stats.p_adjust(FloatVector(p_val_2_list), method=p_adj_method)

    return p_val_1_adjusted, p_val_2_adjusted

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

    df = df[((df["Date"] >= start_date) & (df["Date"] <= end_date))]

    # if AvgW or AvgL is null, replace with B365 odds
    df['AvgW'] = df['AvgW'].fillna(df['B365W'])
    df['AvgL'] = df['AvgL'].fillna(df['B365L'])

    if args.player_1 == 'all' and args.player_2 == 'all':
        mesh = np.array(np.meshgrid(df["P_i"].unique(), df["P_j"].unique()))
        combinations = mesh.T.reshape(-1, 2)
    elif args.player_1 != 'all' and args.player_2 == 'all':
        mesh = np.array(np.meshgrid(np.array(args.player_1), df["P_j"].unique()))
        combinations = mesh.T.reshape(-1, 2)
    elif args.player_1 == 'all' and args.player_2 != 'all':
        mesh = np.array(np.meshgrid(df["P_i"].unique(), np.array(args.player_2)))
        combinations = mesh.T.reshape(-1, 2)
    elif args.player_1 != 'all' and args.player_2 != 'all':
        mesh = np.array(np.meshgrid(np.array(args.player_1), np.array(args.player_2)))
        combinations = mesh.T.reshape(-1, 2)

    header = ['player1', 'player2', 'results_set', 'runs', 'num_Ns', 'num_ULs', 'num_UWs', 'Z_stat', 'p_val_1', 'p_val_2']
    with open('bogey_results.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        existing_pairs = set()  # Create an empty set to store existing player pairs
        
        for i in range(len(combinations)):
            print(str(i + 1) + ' of ' + str(len(combinations)) + ' iterations (' + str(round((i/len(combinations))*100,1)) + '% complete)')
            p1 = pd.DataFrame(combinations).iloc[i][0]
            p2 = pd.DataFrame(combinations).iloc[i][1]
            
            # sort the players to ensure we are checking the same player pair, regardless of order
            p1, p2 = (p1, p2) if p1 < p2 else (p2, p1) 
            player_pair = (p1, p2) 
            
            # Check if the player pair already exists in the set
            if player_pair in existing_pairs:
                continue  # if it does, skip to the next iteration
            else:
                existing_pairs.add(player_pair)  # if it does not, add it to the set
                
            df_p1_p2 = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1))]

            if len(df_p1_p2) == 0:
                continue

            # match results for the given parameters
            RS = get_ur_list(p1, p2, df_p1_p2)[0]
            # corresponding match dates
            RS_date_list = get_ur_list(p1, p2, df_p1_p2)[1]

            # Gather info
            numRuns = getRuns(RS) # Grab streaks in the data

            if numRuns == 1 and len(combinations) > 1:
                continue
            elif numRuns == 1 and len(combinations) == 1:
                (pd.DataFrame.from_records(list_of_tuples(RS_date_list, RS), columns =['Date', 'Result']).to_string(index=False))

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
            ww_z_k_3 = WW_runs_test_k_3(R, n1, n2, n3, n, args.z_val_type)

            # calculate p-values
            p_values_one = st.norm.sf(abs(ww_z_k_3))   # one-sided
            p_values_two = st.norm.sf(abs(ww_z_k_3))*2 # two-sided

            data = [str(p1), str(p2), list_of_tuples(RS_date_list, RS), R, n1, n2, n3, ww_z_k_3, p_values_one, p_values_two]
            
            writer.writerow(data)
        
        f.flush()

        p_val_csv = pd.read_csv('bogey_results.csv')
        p_val_csv['p_val_1_adj'] = 0.0
        p_val_csv['p_val_2_adj'] = 0.0

        p_val_1_adj, p_val_2_adj = adjust_pvalues(p_val_csv, args.p_adj_method)

        p_val_csv.iloc[:, -2] = p_val_1_adj
        p_val_csv.iloc[:, -1] = p_val_2_adj

        p_val_csv.to_csv('bogey_results_adj.csv', index=False)
    
    f.close()

    # Also print results if only running for player pair
    if args.player_1 != 'all' and args.player_2 != 'all':
        print(str(p1) + ' vs. ' + str(p2))
        print('==== RESULTS ====')
        print('Results set (RS):')
        print(pd.DataFrame.from_records(list_of_tuples(RS_date_list, RS), columns =['Date', 'Result']).to_string(index=False))
        print()
        print('k-Category Wald-Wolfowitz Runs Test (k = 3)')
        print('Number of runs: %s' %(R))
        print('Number of Ns: %s; Number of ULs: %s; Number of UWs: %s ' %(n1,n2,n3))
        print('Z value: %s' %(ww_z_k_3))
        print('One tailed P value: %s; Two tailed P value: %s ' %(p_values_one, p_values_two))

if __name__ == '__main__':
    main()
