#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 15:11:45 2022

@author: rorybunker
"""
# Nishikori K. - Tsonga J.W. 0.03234427190062463    0.06331522897380863  ['UW', 'UW', 'UW', 'UL', 'UL']
# https://www.heraldsun.com.au/sport/tennis/jowilfried-tsonga-hopes-to-avoid-australian-open-bogey-kei-nishikori/news-story/2dfaab3f641494447405ae65fc7e7592

import pandas as pd

df = pd.read_csv('Data_Clean.csv', low_memory=False)
# uncomment if you only want to consider Grand Slams
# df = df[(df["Tournament"] == "Australian Open")]
# df = df[(df["Series"] == "Grand Slam")]

p1 = 'Nishikori K.'
p2 = 'Tsonga J.W.'

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
