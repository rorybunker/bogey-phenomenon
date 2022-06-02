#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 15:11:45 2022
@author: rorybunker
"""

# Nishikori K. - Tsonga J.W. 1-tailed p-val: 0.03234427190062463  2-tailed p-val: 0.06331522897380863  UR: ['UW', 'UW', 'UW', 'UL', 'UL']
# https://www.heraldsun.com.au/sport/tennis/jowilfried-tsonga-hopes-to-avoid-australian-open-bogey-kei-nishikori/news-story/2dfaab3f641494447405ae65fc7e7592

import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/rorybunker/bogey-teams-players-sport/main/Data_Clean.csv', low_memory=False)
# uncomment any of the below if applicable
# df = df[(df["Tournament"] == "Australian Open")]
# df = df[(df["Series"] == "Grand Slam")]
# df = df[(df["Date"] <= "2017-01-12")]
p2 = 'Nishikori K.'
p1 = 'Tsonga J.W.'

df_p1_p2 = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1))]

def check_hr_set(df_p1_p2):
    if (1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1) or (1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2):
        return "U"
    else:
        return "N"
    
def add_upset_type_column1(df_p1_p2):
    
    if 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1:
        return "UW"
    elif 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2:
        return "UL"
    else:
        return "N"
    
def add_upset_type_column2(df_p1_p2):
    if 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p2:
        return "UW"
    elif 1/df_p1_p2["AvgW"] < 1/df_p1_p2["AvgL"] and df_p1_p2['Winner'] == p1:
        return "UL"
    else:
        return "N"
  
def get_hr_list(df_p1_p2):
    df_p1_p2["hr_check"] = df_p1_p2.apply(lambda x: check_hr_set(x), axis = 1)
    hr_list = []
    
    for val in df_p1_p2["hr_check"]:
        hr_list.append(val)
    
    return hr_list

def get_ur_list(df_p1_p2):
    df_p1_p2["upset_type_p1"] = df_p1_p2.apply(lambda x: add_upset_type_column1(x), axis = 1)
    df_p1_p2["upset_type_p2"] = df_p1_p2.apply(lambda x: add_upset_type_column2(x), axis = 1)
    
    ur_list = []
    for r in df_p1_p2["upset_type_p1"]:
        if r != 'N':
            ur_list.append(r)
 
    return ur_list

# Wald-Wolfowitz Runs Test (Actual)
# Adapted from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

import math
import scipy.stats as st # for pvalue 
import numpy as np
# import os
# path = '/Users/rorybunker/Google Drive/Research/Bogey Teams in Sport/Data'
# os. chdir(path) 

df_player1_player2 = df_p1_p2
L = get_hr_list(df_player1_player2)

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

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

# Gather info 
numRuns = getRuns(L) # Grab streaks in the data

L_unique = unique(L)

u1 = []
u2 = []
for u in L:
    if u == L_unique[0]:
        u1.append(u)
    elif u == L_unique[1]:
        u2.append(u)

# Define parameters
R = numRuns      # number of runs
n1 = len(u1)        # number of 'NOT UPSET'
n2 = len(u2)        # number of 'UPSET NOT WIN'
n = n1 + n2      # should equal len(L)

# Run the test
ww_z = WW_runs_test(R, n1, n2, n)

# test the pvalue
p_values_one = st.norm.sf(abs(ww_z))   #one-sided
p_values_two = st.norm.sf(abs(ww_z))*2 #twosided

# Print results
print('Wald-Wolfowitz Runs Test')
print('Number of runs: %s' %(R))
print('Number of 1\'s: %s; Number of 0\'s: %s ' %(n1,n2))
print('Z value: %s' %(ww_z))
print('One tailed P value: %s; Two tailed P value: %s ' %(p_values_one, p_values_two))

if p_values_one < 0.05:
    ur = get_ur_list(df_player1_player2)

print(ur)

ul_count = 0
uw_count = 0

for r in ur:
    if r == 'UW':
        uw_count += 1
    else:
        ul_count += 1

print(uw_count)
print(ul_count)
print(uw_count/(uw_count+ul_count))
print(uw_count/len(df_player1_player2))
print(ul_count/len(df_player1_player2))
