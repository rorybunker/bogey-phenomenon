"""
Bogey player identification method using data from professional men's tennis.
The data, Data_Clean.csv, is the same dataset Angelini et al. (2022), which
had been passed through the clean() function in the authors' welo R package
using the create_data_clean_csv_files.R script
"""

import csv
import pandas as pd
import numpy as np
import warnings
import argparse
from datetime import datetime
import ast
import os
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

def add_upset_type_column1(p1, p2, match_df):
    # Check if the implied win probability for the loser is higher than the implied win probability for the winner,
    # indicating a potential upset
    if 1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p1:
        return "UW"  # Upset win for p1
    elif 1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p2:
        return "UL"  # Upset loss for p2
    else:
        return "N"  # Non-upset

def add_upset_type_column2(p1, p2, match_df):
    # Check if the implied win probability for the loser is higher than the implied win probability for the winner,
    # indicating a potential upset
    if 1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p2:
        return "UW"  # Upset win for p2
    elif 1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p1:
        return "UL"  # Upset loss for p1
    else:
        return "N"  # Non-upset

def get_winner(p1, p2, match_df):
    match_result_list = []
    for winner in match_df['Winner']:
        if winner == p1:
            match_result_list.append('p1')
        elif winner == p2:
            match_result_list.append('p2')
    return match_result_list

def get_upset_result_list(p1, p2, match_df):
    """
    Extracts the upset types and dates from the match_df DataFrame for matches between players p1 and p2 
    by utilizing the add_upset_type_column1 and add_upset_type_column2 functions. 
    The upset types are stored in the upset_result_list, and the dates are returned as a separate list.
    
    Parameters:
    - p1 (str): Player 1
    - p2 (str): Player 2
    - match_df (DataFrame): DataFrame containing matches between p1 and p2
    
    Returns:
    - upset_result_list (list): List containing the upset types
    - list(match_df['Date']) (list): List of dates corresponding to the matches between p1 and p2.
    """
    
    # Add two columns to the match_df DataFrame: "upset_type_p1" and "upset_type_p2"
    # Values in these columns are determined by applying the add_upset_type_column1 and add_upset_type_column2 functions,
    # respectively, to each row of the DataFrame
    match_df["upset_type_p1"] = match_df.apply(lambda x: add_upset_type_column1(p1, p2, x), axis=1)
    match_df["upset_type_p2"] = match_df.apply(lambda x: add_upset_type_column2(p1, p2, x), axis=1)

    upset_result_list = []
    # Iterate over the values in the "upset_type_p1" column of the DataFrame
    # If the value is not equal to 'N' (non-upset), append it to upset_result_list
    for r in match_df["upset_type_p1"]:
        if r != 'N':
            upset_result_list.append(r)

    return upset_result_list, list(match_df['Date'])

# Function to check if a match result is an upset or non-upset
# Returns "U" for upset and "N" for non-upset
def check_upset_nonupset_results(p1, p2, match_df):
    if (1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p1) or (1/match_df["AvgW"] < 1/match_df["AvgL"] and match_df['Winner'] == p2):
        return "U" # Upset
    else:
        return "N" # Non-upset

# Function to get the historical results list (upset or non-upset) and the corresponding dates
def get_historical_results_list(p1, p2, match_df):
    # Add a column to the DataFrame with the upset/non-upset results using check_upset_nonupset_results function
    match_df["hr_check"] = match_df.apply(lambda x: check_upset_nonupset_results(p1, p2, x), axis=1) 
    
    results_list = list(match_df['hr_check'])
    dates_list = list(match_df['Date'])
    time_diff_list = []

    for i in range(1, len(dates_list)):
        if args.dataset == 'atp':
            date1 = datetime.strptime(dates_list[i-1], '%Y-%m-%d')
            date2 = datetime.strptime(dates_list[i], '%Y-%m-%d')
        elif args.dataset == 'wta':
            date1 = datetime.strptime(dates_list[i-1], '%d/%m/%Y')
            date2 = datetime.strptime(dates_list[i], '%d/%m/%Y')
        time_diff = (date2 - date1).days
        time_diff_list.append(time_diff)

    return results_list, dates_list, time_diff_list

# Function to create a list of tuples from two input lists
def list_of_tuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

def adjust_pvalues(p_val_csv, p_adj_method):
    from rpy2.robjects.packages import importr
    from rpy2.robjects.vectors import FloatVector
    stats = importr('stats')
    p_val_list = p_val_csv['p_value_fisher'].tolist()
    p_val_1_adjusted = stats.p_adjust(FloatVector(p_val_list), method=p_adj_method)
    return p_val_1_adjusted

# Function to determine wins and losses for a player
def get_wins_losses(player, matches_df):
    player_matches = matches_df[(matches_df['Winner'] == player) | (matches_df['Loser'] == player)]
    wins = len(player_matches[player_matches['Winner'] == player]['Winner'])
    losses = len(player_matches[player_matches['Loser'] == player]['Loser'])
    return wins, losses

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

    # Construct the filename
    filename = 'bogey_results_output' + '_' + args.dataset + '_' + args.upset
    if args.grand_slam == 0:
        filename += '_nongrandslam'
    elif args.grand_slam == 1:
        filename += '_grandslam'
    filename += '.csv'
    header = ['player1', 'player2', 'match_results', 'results_set', 'upset_results', 'results_set_with_dates', 'upset_results_set_with_dates', 'or', 'p_value_fisher', 'expected_wins_p1', 'expected_wins_p2', 'actual_wins_p1', 'actual_wins_p2']
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        # Create an empty set to store existing player pairs
        existing_pairs = set() 
        
        for i in range(len(combinations)):
            print(str(i + 1) + ' of ' + str(len(combinations)) + ' iterations (' + str(round((i/len(combinations))*100,1)) + '% complete)')
            
            p1 = pd.DataFrame(combinations).iloc[i][0]
            p2 = pd.DataFrame(combinations).iloc[i][1]
            
            # Sort the players to ensure we are checking the same player pair, regardless of order
            p1, p2 = (p1, p2) if p1 < p2 else (p2, p1) 
            player_pair = (p1, p2) 
            
            # Check if the player pair already exists in the set
            if player_pair in existing_pairs:
                continue  # if it does, skip to the next iteration
            else:
                existing_pairs.add(player_pair)  # if it does not, add it to the set
            
            # Get all historical matches between player 1 and player 2
            match_df = df[((df["Winner"] == p1) & (df["Loser"] == p2)) | ((df["Winner"] == p2) & (df["Loser"] == p1))]

            # If there have been no historical matches between player 1 and player 2, continue
            if len(match_df) == 0:
                continue

            historical_results, historical_results_dates, time_diffs = get_historical_results_list(p1, p2, match_df)

            # Considering only the upset results, get the set of upset types — upset wins and upset losses — between the two players
            upset_results = get_upset_result_list(p1, p2, match_df)[0]
            upset_results_dates = get_upset_result_list(p1, p2, match_df)[1]

            # ---------- Conduct the chi-squared test ----------
            from scipy.stats import fisher_exact

            
            # Get the number of wins and losses for each player
            player1_wins, player2_wins = get_wins_losses(p1, match_df)
            
            match_results_list = get_winner(p1, p2, match_df)

            if args.upset == 'odds':
                # Get the odds for each player in the matches between the pair of players
                player1_odds = pd.concat([match_df.loc[((match_df['Winner'] == p1) & (match_df['Loser'] == p2)), 'AvgW'], match_df.loc[((match_df['Winner'] == p2) & (match_df['Loser'] == p1)), 'AvgL']])
                player2_odds = pd.concat([match_df.loc[((match_df['Winner'] == p2) & (match_df['Loser'] == p1)), 'AvgW'], match_df.loc[((match_df['Winner'] == p1) & (match_df['Loser'] == p2)), 'AvgL']])

                # Convert the odds into probabilities
                player1_win_prob = 1 / player1_odds
                player2_win_prob = 1 / player2_odds

                # Calculate the normalization factor
                total_probability = player1_win_prob + player2_win_prob

                # Normalize the probabilities
                player1_win_prob_norm = player1_win_prob / total_probability
                player2_win_prob_norm = player2_win_prob / total_probability

                # Calculate the expected number of matches won based on the sum of the betting odds-implied probabilities
                # represents the expected numbers of matches the player should win given the betting odds distribution.
                expected_matches_won_p1 = np.sum(player1_win_prob_norm)
                expected_matches_won_p2 = np.sum(player2_win_prob_norm)
                
            elif args.upset == 'elo':
                # Get the pre-match Elo ratings for each player in the matchup
                player1_elo = pd.concat([match_df.loc[((match_df['P_i'] == p1) & (match_df['P_j'] == p2)), 'Elo_i_before_match'], match_df.loc[((match_df['P_i'] == p2) & (match_df['P_j'] == p1)), 'Elo_j_before_match']])
                player2_elo = pd.concat([match_df.loc[((match_df['P_i'] == p2) & (match_df['P_j'] == p1)), 'Elo_i_before_match'], match_df.loc[((match_df['P_i'] == p1) & (match_df['P_j'] == p2)), 'Elo_j_before_match']])

                # Convert the Elo ratings into win probabilities
                player1_win_prob = (10 ** (player1_elo/400)) / ((10 ** (player1_elo/400)) + (10 ** (player2_elo/400)))
                player2_win_prob = (10 ** (player2_elo/400)) / ((10 ** (player1_elo/400)) + (10 ** (player2_elo/400)))

                # Calculate the expected number of matches won based on the player rankings
                expected_matches_won_p1 = np.sum(player1_win_prob)
                expected_matches_won_p2 = np.sum(player2_win_prob)

            # Create the contingency table
            observed = np.array([[expected_matches_won_p1, player1_wins],
                                    [expected_matches_won_p2, player2_wins]])

            # Perform Fisher's exact test on the contingency table
            oddsratio, p_val_fisher = fisher_exact(observed)

            data = [str(p1), str(p2), match_results_list, historical_results, upset_results, historical_results_dates, upset_results_dates, oddsratio, p_val_fisher, expected_matches_won_p1, expected_matches_won_p2, player1_wins, player2_wins]

            writer.writerow(data)
            f.flush()

        def safely_parse_list(lst):
            try:
                return ast.literal_eval(lst)
            except (SyntaxError, ValueError):
                return []

        # Function to extract non-date elements from the list of tuples
        def extract_non_date(lst):
            return [item[0] for item in lst]

        data = pd.read_csv(filename)

        # Apply the safely_parse_list function to 'results_set_with_dates' column
        data['results_set_with_dates'] = data['results_set_with_dates'].apply(safely_parse_list)
        data['upset_results_set_with_dates'] = data['upset_results_set_with_dates'].apply(safely_parse_list)

        # Extract non-date elements and store them in a new column
        data['results_set'] = data['results_set_with_dates'].apply(extract_non_date)
        data['upset_results_set'] = data['upset_results_set_with_dates'].apply(extract_non_date)

        # Calculate the metrics for each row
        data['total_matches'] = data['results_set_with_dates'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        data['upset_matches'] = data['results_set_with_dates'].apply(lambda x: sum([1 for result in x if result[0] == 'U']))

        # Calculate the number of upset wins and losses
        data['upset_wins'] = data['upset_results_set'].apply(lambda x: x.count('UW'))
        data['upset_losses'] = data['upset_results_set'].apply(lambda x: x.count('UL'))

        # Calculate the upset percentage, upset win percentage, and upset loss percentage
        data['upset_percentage'] = (data['upset_matches'] / data['total_matches']) * 100
        data['upset_win_percentage'] = (data['upset_wins'] / data['upset_matches']) * 100
        data['upset_loss_percentage'] = (data['upset_losses'] / data['upset_matches']) * 100

        # Save the updated data to a new CSV file
        file_prefix = os.path.splitext(filename)[0]
        data.to_csv(file_prefix + '_metrics.csv', index=False)

if __name__ == '__main__':
    main()
