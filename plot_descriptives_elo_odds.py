import csv
import pandas as pd
import numpy as np
import warnings
import argparse
from datetime import datetime
import ast
import os
import seaborn as sns
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-p1', '--player_1', type=str, required=False, default='all', help='player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)')
parser.add_argument('-p2', '--player_2', type=str, required=False, default='all', help='player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)')
parser.add_argument('-d', '--dataset', type=str, required=True, help='atp or wta')
parser.add_argument('-g', '--grand_slam', type=int, required=False, default=2, help='0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)')
parser.add_argument('-t', '--tournament', type=str, required=False, default='all', help='tournament name, e.g., Australian Open')
parser.add_argument('-s', '--s_date', type=str, required=False, default='min', help='start date in YYYY-MM-DD format (default = min date in dataset)')
parser.add_argument('-e', '--e_date', type=str, required=False, default='max', help='end date in YYYY-MM-DD format (default = max date in dataset)')
parser.add_argument('-p', '--p_adj_method', type=str, required=False, default='BH', help='p-value adjustment for multiple comparisons method, e.g., bonferroni, hochberg, BH, holm, hommel, BY')
parser.add_argument('-u', '--upset', type=str, required=False, choices=['odds','elo'], default='odds', help='whether an unexpected result is based on the betting odds or elo rating (default=odds)')
args, _ = parser.parse_known_args()

def main():
    if args.dataset == 'test':
        df = pd.read_csv('Data_Clean_Test.csv', low_memory=False)
    elif args.dataset == 'wta':
        df = pd.read_csv('Data_Clean_WTA.csv', low_memory=False)
    elif args.dataset == 'atp':
        df = pd.read_csv('Data_Clean_ATP_Elo_WElo.csv', low_memory=False)

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
    
    # Restrict the dataframe to be between start date and end date
    df = df[((df["Date"] >= start_date) & (df["Date"] <= end_date))]

    # if AvgW or AvgL is null, replace with B365 odds
    df['AvgW'] = df['AvgW'].fillna(df['B365W'])
    df['AvgL'] = df['AvgL'].fillna(df['B365L'])
    if args.dataset == 'wta':
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    elif args.dataset == 'atp':
        df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.to_period('Y')

    # Combine Elo ratings into a single column
    df_elo_melted = df.melt(id_vars=['Year'], value_vars=['Elo_i_after_match', 'Elo_j_after_match'], var_name='Elo_Type', value_name='Elo_rating')

    # Combine betting odds into a single column
    df_odds_melted = df.melt(id_vars=['Year'], value_vars=['AvgW', 'AvgL'], var_name='Odds_Type', value_name='Betting_odds')

    # Group the data by year
    grouped = df.groupby(['Year'])
    grouped_elo = df_elo_melted.groupby(['Year'])
    grouped_odds = df_odds_melted.groupby(['Year'])

    # Calculate the variance and mean for Elo ratings and betting odds within each group
    agg_winner_df = grouped.agg({
                            'AvgW': ['mean', 'var'],
                            'AvgL': ['mean', 'var']}).reset_index()
    
    agg_elo_df = grouped_elo.agg({
                            'Elo_rating': ['mean', 'var']}).reset_index()

    agg_odds_df = grouped_odds.agg({
                            'Betting_odds': ['mean', 'var']}).reset_index()

    # Rename columns for clarity
    agg_winner_df.columns = ['Year', 'Betting_Win_Odds_mean', 'Betting_Win_Odds_variance', 'Betting_Lose_Odds_mean', 'Betting_Lose_Odds_variance']
    agg_elo_df.columns = ['Year', 'Elo_mean', 'Elo_variance']
    agg_odds_df.columns = ['Year', 'Betting_Odds_mean', 'Betting_Odds_variance']

    # Calculate the combined mean and variance for betting odds
    combined_mean = agg_odds_df['Betting_Odds_mean']
    # combined_mean = (agg_winner_df['Betting_Win_Odds_mean'] + agg_winner_df['Betting_Lose_Odds_mean']) / 2
    combined_variance = agg_odds_df['Betting_Odds_variance']
    # combined_variance = (agg_winner_df['Betting_Win_Odds_variance'] + agg_winner_df['Betting_Lose_Odds_variance']) / 2

    # Calculate the coefficient of variation for Elo and Betting odds
    agg_elo_df['Elo_CV'] = np.sqrt(agg_elo_df['Elo_variance']) / agg_elo_df['Elo_mean']
    agg_winner_df['Betting_Win_Odds_CV'] = np.sqrt(agg_winner_df['Betting_Win_Odds_variance']) / agg_winner_df['Betting_Win_Odds_mean']
    agg_winner_df['Betting_Lose_Odds_CV'] = np.sqrt(agg_winner_df['Betting_Lose_Odds_variance']) / agg_winner_df['Betting_Lose_Odds_mean']
    agg_winner_df['Combined_Odds_CV'] = np.sqrt(combined_variance) / combined_mean
    
    # Filter out NaN values
    agg_elo_df_filtered = agg_elo_df.dropna()
    agg_winner_df_filtered = agg_winner_df.dropna()
    agg_odds_df_filtered = agg_odds_df.dropna()

    # Plotting the CVs
    plt.figure(figsize=(12, 6))
    plt.plot(agg_elo_df_filtered['Year'].astype(str), agg_elo_df_filtered['Elo_CV'], marker='o', label='Elo CV')
    plt.plot(agg_winner_df_filtered['Year'].astype(str), agg_winner_df_filtered['Betting_Win_Odds_CV'], marker='o', label='Betting Win Odds CV')
    plt.plot(agg_winner_df_filtered['Year'].astype(str), agg_winner_df_filtered['Betting_Lose_Odds_CV'], marker='o', label='Betting Lose Odds CV')
    plt.plot(agg_winner_df_filtered['Year'].astype(str), agg_winner_df_filtered['Combined_Odds_CV'], marker='o', label='Combined Odds CV')

    plt.xlabel('Year')
    plt.ylabel('Coefficient of Variation (CV)')
    if args.grand_slam == 1:
        plt.title('Yearly Coefficient of Variation (CV) for Betting Odds and Elo Ratings' + ' - ' + args.dataset + ' - ' + 'Grand Slam')
    elif args.grand_slam == 0:
        plt.title('Yearly Coefficient of Variation (CV) for Betting Odds and Elo Ratings' + ' - ' + args.dataset + ' - ' + 'Non Grand Slam')
    else:
        plt.title('Yearly Coefficient of Variation (CV) for Betting Odds and Elo Ratings' + ' - ' + args.dataset)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Create figure and axes objects
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot Elo mean
    ax1.plot(agg_elo_df_filtered['Year'].astype(str), agg_elo_df_filtered['Elo_mean'], marker='o', color='b', label='Elo Mean')
    ax1.set_ylabel('Elo Mean')
    # ax1.set_title('Elo Mean and CV Over Time')
    if args.grand_slam == 1:
        ax1.set_title('Elo Mean and CV Over Time' + ' - ' + args.dataset + ' - ' + 'Grand Slam')
    elif args.grand_slam == 0:
        ax1.set_title('Elo Mean and CV Over Time' + ' - ' + args.dataset + ' - ' + 'Non Grand Slam')
    else:
        ax1.set_title('Elo Mean and CV Over Time' + ' - ' + args.dataset)

    # Plot Elo variance
    ax2.plot(agg_elo_df_filtered['Year'].astype(str), agg_elo_df_filtered['Elo_CV'], marker='o', color='r', label='Elo CV')
    ax2.set_ylabel('Elo CV')
    ax2.set_xlabel('Year')

    # Show legend and grid
    ax1.legend()
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Show plot
    plt.show()

   # Create figure and axes objects
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot Winner Odds mean
    ax1.plot(agg_winner_df_filtered['Year'].astype(str), agg_winner_df_filtered['Betting_Win_Odds_mean'], marker='o', color='b', label='Winner Odds Mean')
    ax1.set_ylabel('Odds Mean')
    if args.grand_slam == 1:
        ax1.set_title('Odds Mean and CV Over Time' + ' - ' + args.dataset + ' - ' + 'Grand Slam')
    elif args.grand_slam == 0:
        ax1.set_title('Mean and CV Over Time' + ' - ' + args.dataset + ' - ' + 'Non Grand Slam')
    else:
        ax1.set_title('Odds Mean and CV Over Time' + ' - ' + args.dataset)

    # Plot Loser Odds mean
    ax1.plot(agg_winner_df_filtered['Year'].astype(str), agg_winner_df_filtered['Betting_Lose_Odds_mean'], marker='o', color='r', label='Loser Odds Mean')

    # Plot Combined Odds mean
    ax1.plot(agg_winner_df_filtered['Year'].astype(str), combined_mean, marker='o', color='g', label='Combined Odds Mean')

    # Plot Winner Odds CV (square root of variance)
    ax2.plot(agg_winner_df_filtered['Year'].astype(str), np.sqrt(agg_winner_df_filtered['Betting_Win_Odds_variance']), marker='o', color='b', label='Winner Odds CV')
    ax2.set_ylabel('Odds CV')
    ax2.set_xlabel('Year')

    # Plot Loser Odds CV (square root of variance)
    ax2.plot(agg_winner_df_filtered['Year'].astype(str), np.sqrt(agg_winner_df_filtered['Betting_Lose_Odds_variance']), marker='o', color='r', label='Loser Odds CV')

    # Plot Combined Odds CV (square root of variance)
    ax2.plot(agg_winner_df_filtered['Year'].astype(str), np.sqrt(combined_variance), marker='o', color='g', label='Combined Odds CV')

    # Show legend and grid
    ax1.legend()
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Show plot
    plt.show()

if __name__ == "__main__":
    main()
