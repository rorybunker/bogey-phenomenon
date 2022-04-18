#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 15:11:45 2022

@author: rorybunker
"""

import os
import sqlite3
import pandas as pd

os.chdir('/Users/rorybunker/Google Drive/Research/Bogey Teams in Sport/Data')

def get_team_id(team_name):
    """
    Returns the team id for a given team_name using the Team table. 

    Parameters
    ----------
    team_name : string (enclosed in single quotes)
        DESCRIPTION.

    Returns
    -------
    int
        team id of the corresponding team name (if exists)

    """
    try:
        sqliteConnection = sqlite3.connect('database.sqlite')
        cursor = sqliteConnection.cursor()
        print("Database created and Successfully Connected to SQLite")
    
        sqlite_select_Query = "select distinct team_api_id from Team where team_long_name = '" + team_name + "';"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        if len(record) == 0:
            print("ERROR: there is no id associated with that team name!")
            exit
        else:
            print("The team_id of this team is: ", record[0][0])
        cursor.close()
    
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    return record[0][0]

def get_team_matches(team_id):
    """
    Returns a dataframe that is a subset of the Match table for a given team id

    Parameters
    ----------
    team_id : int
        team_id, e.g., obtained from the get_team_id(team_name) function.

    Returns
    -------
    db_df : pandas dataframe
        subset of the Match table for the input team id.

    """
    try:
        sqliteConnection = sqlite3.connect('database.sqlite')
        print("Database created and Successfully Connected to SQLite")
        conn = sqlite3.connect('database.sqlite', isolation_level=None,
                               detect_types=sqlite3.PARSE_COLNAMES)
        db_df = pd.read_sql_query("SELECT * FROM Match WHERE home_team_api_id = " + str(team_id) + " OR away_team_api_id = " + str(team_id) + " ORDER BY date ASC", conn)
        
        if len(db_df) == 0:
            print("ERROR: no records found for team_id " + str(team_id))
            exit
        
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    
    return db_df

def add_result_column(df):
    if ((df['team_venue'] == 'HOME' and df['home_team_goal'] > df['away_team_goal']) 
        or (df['team_venue'] == 'AWAY' and df['home_team_goal'] < df['away_team_goal'])):
        return "WIN"
    else:
        return "NOT WIN"

def add_upset_type_column(df):
    if (df["home_implied_win_prob"] > df["away_implied_win_prob"] and df['team_venue'] == 'HOME' and df["result"] == 'NOT WIN') or (df["home_implied_win_prob"] < df["away_implied_win_prob"] and df['team_venue'] == 'AWAY' and df["result"] == 'NOT WIN'):
        return "UPSET NOT WIN"
    elif (df["home_implied_win_prob"] < df["away_implied_win_prob"] and df['team_venue'] == 'HOME' and df["result"] == 'WIN') or (df["home_implied_win_prob"] > df["away_implied_win_prob"] and df['team_venue'] == 'AWAY' and df["result"] == 'WIN'):
        return "UPSET WIN"
    else:
        return "NOT UPSET"
    

team_name = 'Manchester United'
team_id = get_team_id(team_name)
    
df = get_team_matches(team_id)
    
df['team_venue'] = ['HOME' if x == team_id else 'AWAY' for x in df['home_team_api_id']]
df["result"] = df.apply(lambda x: add_result_column(x), axis = 1)
df["home_odds_avg"] = df[['B365H', 'BWH', 'IWH', 'LBH', 'PSH', 'WHH',
                            'SJH', 'VCH', 'GBH', 'BSH']].mean(axis=1)
df["home_implied_win_prob"] = 1/df["home_odds_avg"]
df["away_odds_avg"] = df[['B365A', 'BWA', 'IWA', 'LBA', 'PSA', 'WHA',
                            'SJA', 'VCA', 'GBA', 'BSA']].mean(axis=1)
df["away_implied_win_prob"] = 1/df["away_odds_avg"]
df["upset_type"] = df.apply(lambda x: add_upset_type_column(x), axis = 1)
    
comparison_team_name = 'Liverpool'
team_id = get_team_id(comparison_team_name)

df = df[(df["home_team_api_id"] == team_id) | (df["away_team_api_id"] == team_id)]

#df.to_csv(team_name + '_matches.csv', index=False)
