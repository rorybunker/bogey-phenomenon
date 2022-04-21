#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 15:11:45 2022

@author: rorybunker
"""

import pandas as pd

df = pd.read_csv('/Users/rorybunker/Google Drive/Research/Bogey Teams in Sport/Data/Data_Clean.csv', low_memory=False)
# uncomment if you only want to consider Grand Slams
# df = df[(df["Series"] == "Grand Slam")]

p1 = 'Djokovic N.'
p2 = 'Murray A.'

def add_upset_type_column1(df):
    
    if 1/df["AvgW"] < 1/df["AvgL"] and df['Winner'] == p1:
        return "UW"
    elif 1/df["AvgW"] < 1/df["AvgL"] and df['Winner'] == p2:
        return "UL"
    else:
        return "N"
    
def add_upset_type_column2(df):
    
    if 1/df["AvgW"] < 1/df["AvgL"] and df['Winner'] == p2:
        return "UW"
    elif 1/df["AvgW"] < 1/df["AvgL"] and df['Winner'] == p1:
        return "UL"
    else:
        return "N"

df = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1)) ]
    
df["upset_type_p1"] = df.apply(lambda x: add_upset_type_column1(x), axis = 1)
df["upset_type_p2"] = df.apply(lambda x: add_upset_type_column2(x), axis = 1)
 
upset_type_list1 = []
for val in df['upset_type_p1']:
    if val == 'UW':
        val = 'N'
    upset_type_list1.append(val)

upset_type_list2 = []
for val in df['upset_type_p2']:
    if val == 'UW':
        val = 'N'
    upset_type_list2.append(val)
    
print(upset_type_list1)
print("")
print(upset_type_list2)
