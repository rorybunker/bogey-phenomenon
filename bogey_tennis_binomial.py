"""
Bogey player identification method using data from professional men's tennis.
The data, Data_Clean.csv, is the same dataset Angelini et al. (2022), which
had been passed through the clean() function in the authors' welo R package
"""

import csv
import pandas as pd
import numpy as np
import warnings
import argparse
from scipy.stats import binom_test
from datetime import datetime
import ast
pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-p1', '--player_1', type=str, required=False, default='all', help='player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)')
parser.add_argument('-p2', '--player_2', type=str, required=False, default='all', help='player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)')
parser.add_argument('-d', '--dataset', type=str, required=True, help='atp (mens) or wta (womens) or test')
parser.add_argument('-g', '--grand_slam', type=int, required=False, default=2, help='0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)')
parser.add_argument('-t', '--tournament', type=str, required=False, default='all', help='tournament name, e.g., Australian Open')
parser.add_argument('-s', '--s_date', type=str, required=False, default='min', help='start date in YYYY-MM-DD format (default = min date in dataset)')
parser.add_argument('-e', '--e_date', type=str, required=False, default='max', help='end date in YYYY-MM-DD format (default = max date in dataset)')
parser.add_argument('-p', '--p_adj_method', type=str, required=False, default='BH', help='p-value adjustment for multiple comparisons method, e.g., bonferroni, hochberg, BH, holm, hommel, BY')
parser.add_argument('-alpha', '--sig_level', type=float, required=False, default=0.05, help='level of statistical significance, alpha. Default is alpha = 0.05')
args, _ = parser.parse_known_args()

def add_upset_type_column1(p1, p2, p1_p2_matches_df):
    # Check if the implied win probability for the loser is higher than the implied win probability for the winner,
    # indicating a potential upset
    if 1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p1:
        return "UW"  # Upset win for p1
    elif 1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p2:
        return "UL"  # Upset loss for p2
    else:
        return "N"  # Non-upset

def add_upset_type_column2(p1, p2, p1_p2_matches_df):
    # Check if the implied win probability for the loser is higher than the implied win probability for the winner,
    # indicating a potential upset
    if 1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p2:
        return "UW"  # Upset win for p2
    elif 1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p1:
        return "UL"  # Upset loss for p1
    else:
        return "N"  # Non-upset

def get_upset_result_list(p1, p2, p1_p2_matches_df):
    """
    Extracts the upset types and dates from the p1_p2_matches_df DataFrame for matches between players p1 and p2 
    by utilizing the add_upset_type_column1 and add_upset_type_column2 functions. 
    The upset types are stored in the upset_result_list, and the dates are returned as a separate list.
    
    Parameters:
    - p1 (str): Player 1
    - p2 (str): Player 2
    - p1_p2_matches_df (DataFrame): DataFrame containing matches between p1 and p2
    
    Returns:
    - upset_result_list (list): List containing the upset types
    - list(p1_p2_matches_df['Date']) (list): List of dates corresponding to the matches between p1 and p2.
    """
    
    # Add two columns to the p1_p2_matches_df DataFrame: "upset_type_p1" and "upset_type_p2"
    # Values in these columns are determined by applying the add_upset_type_column1 and add_upset_type_column2 functions,
    # respectively, to each row of the DataFrame
    p1_p2_matches_df["upset_type_p1"] = p1_p2_matches_df.apply(lambda x: add_upset_type_column1(p1, p2, x), axis=1)
    p1_p2_matches_df["upset_type_p2"] = p1_p2_matches_df.apply(lambda x: add_upset_type_column2(p1, p2, x), axis=1)

    upset_result_list = []
    # Iterate over the values in the "upset_type_p1" column of the DataFrame
    # If the value is not equal to 'N' (non-upset), append it to upset_result_list
    for r in p1_p2_matches_df["upset_type_p1"]:
        if r != 'N':
            upset_result_list.append(r)

    return upset_result_list, list(p1_p2_matches_df['Date'])

# Function to check if a match result is an upset or non-upset
# Returns "U" for upset and "N" for non-upset
def check_upset_nonupset_results(p1, p2, p1_p2_matches_df):
    if (1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p1) or (1/p1_p2_matches_df["AvgW"] < 1/p1_p2_matches_df["AvgL"] and p1_p2_matches_df['Winner'] == p2):
        return "U" # Upset
    else:
        return "N" # Non-upset

# Function to get the historical results list (upset or non-upset) and the corresponding dates
def get_historical_results_list(p1, p2, p1_p2_matches_df):
    # Add a column to the DataFrame with the upset/non-upset results using check_upset_nonupset_results function
    p1_p2_matches_df["hr_check"] = p1_p2_matches_df.apply(lambda x: check_upset_nonupset_results(p1, p2, x), axis=1) 
    
    results_list = list(p1_p2_matches_df['hr_check'])
    dates_list = list(p1_p2_matches_df['Date'])
    time_diff_list = []

    for i in range(1, len(dates_list)):
        date1 = datetime.strptime(dates_list[i-1], '%Y-%m-%d')
        date2 = datetime.strptime(dates_list[i], '%Y-%m-%d')
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
    p_val_list = p_val_csv['p_value_chisq'].tolist()
    p_val_1_adjusted = stats.p_adjust(FloatVector(p_val_list), method=p_adj_method)
    return p_val_1_adjusted

# Function to determine wins and losses for a player
def get_wins_losses(player, matches_df):
    player_matches = matches_df[(matches_df['P_i'] == player) | (matches_df['P_j'] == player)]
    wins = len(player_matches[player_matches['Winner'] == player]['Winner'])
    losses = len(player_matches[player_matches['Loser'] == player]['Loser'])
    return wins, losses

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

    header = ['player1', 'player2', 'results_set_with_dates', 'upset_results_set_with_dates', 'time_diffs', 'chisq_p1', 'p_value_chisq_p1', 'chisq_p2', 'p_value_chisq_p2']
    with open('bogey_results_binom.csv', 'w', encoding='UTF8', newline='') as f:
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
            p1_p2_matches_df = df[((df["P_i"] == p1) & (df["P_j"] == p2)) | ((df["P_i"] == p2) & (df["P_j"] == p1))]

            # If there have been no historical matches between player 1 and player 2, continue
            if len(p1_p2_matches_df) == 0:
                continue

            historical_results_date_list, historical_results, time_diffs = get_historical_results_list(p1, p2, p1_p2_matches_df)

            # Considering only the upset results, get the set of upset types — upset wins and upset losses — between the two players
            upset_results = get_upset_result_list(p1, p2, p1_p2_matches_df)[0]
            upset_results_date_list = get_upset_result_list(p1, p2, p1_p2_matches_df)[1]

            # ---------- Conduct the chi-squared test ----------
            from scipy.stats import chi2_contingency

            # Add a small constant value to avoid zero frequencies
            epsilon = 1e-8

            # Get the number of wins and losses for each player
            player1_wins, player2_wins = get_wins_losses(p1, p1_p2_matches_df)
            
            # Get the odds for each player in the matches between the pair of players
            player1_odds = p1_p2_matches_df[(p1_p2_matches_df['P_i'] == p1) & (p1_p2_matches_df['P_j'] == p2)]['AvgL']
            player2_odds = p1_p2_matches_df[(p1_p2_matches_df['P_i'] == p2) & (p1_p2_matches_df['P_j'] == p1)]['AvgW']

            # Convert the odds into probabilities
            player1_win_prob = 1 / player1_odds
            player2_win_prob = 1 / player2_odds

            # Calculate the number of matches between the player pair
            num_matches_between_player_pair = player1_wins + player2_wins

            # Calculate the expected frequencies based on the probabilities and the total number of matches
            expected_won_p1 = num_matches_between_player_pair * np.mean(player1_win_prob)
            expected_won_p2 = num_matches_between_player_pair * np.mean(player2_win_prob)
            
            # Add a small constant value to avoid zero frequencies
            epsilon = 1e-8

            # Create the contingency tables with the modified structure
            observed = np.array([[expected_won_p1 + epsilon, player1_wins],
                                    [expected_won_p2 + epsilon, player2_wins]])
            
            # Perform the chi-squared test on each contingency table
            chi2, p_val_chisq, _, _ = chi2_contingency(observed)

            # observed = np.array([[upset_results.count('UW'), upset_results.count('UL')],
            #                     [len(historical_results) - upset_results.count('UW'), len(historical_results) - upset_results.count('UL')]])

            # chi2 = None
            # p_val_chisq = None
            # # Perform the chi-squared test
            # if len(upset_results) > 0:
            # chi2, p_val_chisq, _, _ = chi2_contingency(observed)

            # print("Chi-squared statistic:", chi2)
            # print("p-value:", p_val_chisq)

            # ---------- Conduct Fisher's exact test ----------
            # oddsratio, p_val_fisher = fisher_exact(observed)
            
            data = [str(p1), str(p2), list_of_tuples(historical_results_date_list, historical_results), list_of_tuples(upset_results, upset_results_date_list), time_diffs, chi2, p_val_chisq]

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

        data = pd.read_csv('bogey_results_binom.csv')

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
        data.to_csv('bogey_results_binom_metrics.csv', index=False)

        # ---------- Adjust p-values for multiple comparisons problem ----------
        # Read in the created bogey_results.csv file and create column for the adjusted p-value
        # p_val_csv = pd.read_csv('bogey_results_binom_metrics.csv')
        # p_val_csv['p_val_chisq_adj'] = 0.0

        # # Adjust the p-value
        # p_val_chisq_adj = adjust_pvalues(p_val_csv, args.p_adj_method)

        # # Set the adjusted p-values in the end df column
        # p_val_csv.iloc[:, -1] = p_val_chisq_adj

        # # Export the file with adjusted p-values to a csv
        # p_val_csv.to_csv('bogey_results_binom_metrics_adj.csv', index=False)

        # Also print results if only running for player pair
        if args.player_1 != 'all' and args.player_2 != 'all':
            print(str(p1) + ' vs. ' + str(p2))
            print('==== RESULTS ====')
            print('Results set (upset_results):')
            print(pd.DataFrame.from_records(list_of_tuples(upset_results_date_list, upset_results), columns=['Date', 'Result']).to_string(index=False))
            print()

if __name__ == '__main__':
    main()
