"""
Wald-Wolfowitz Runs Test and Bogey player identification method using
data from professional men's tennis.
The original Wald-Wolfowitz Runs Test portion of this code was
adapted from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

The data, Data_Clean.csv, is the same dataset Angelini et al. (2022), which
had been passed through the clean() function in the authors' welo R package
"""

import csv
import pandas as pd
import math
import scipy.stats as st # for pvalue
import numpy as np
import warnings
import argparse
import sys

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
parser.add_argument('-z', '--z_val_type', type=str, required=False, default='cc', help='type of z statistic - standard std or continuity corrected cc (default = cc)')
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
    p1_p2_matches_df["hr_check"] = p1_p2_matches_df.apply(lambda x: check_upset_nonupset_results(p1, p2, x), axis = 1) 
    return list(p1_p2_matches_df['hr_check']), list(p1_p2_matches_df['Date'])

# Function to create a list of tuples from two input lists
def list_of_tuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

# Finds runs in data: counts and creates a list of them
def get_num_runs(L):
  import itertools
  return len([sum(1 for _ in r) for _, r in itertools.groupby(L)])

# define the WW runs test described above
def WW_runs_test(R, n1, n2, n):
    # compute the standard error of R if the null (random) is true
    standard_error = math.sqrt( ((2*n1*n2) * (2*n1*n2 - n)) / ((n**2)*(n-1)) )

    if standard_error == 0:
        if R == 1:
            return 0  # Special case: R is 1
        else:
            return None  # Unable to calculate z

    # compute the expected value of R if the null is true
    muR = ((2*n1*n2)/n) + 1

    # test statistic: R vs muR
    z = (R - muR)/standard_error

    return z

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

def adjust_pvalues(p_val_csv, p_adj_method):
    from rpy2.robjects.packages import importr
    from rpy2.robjects.vectors import FloatVector

    stats = importr('stats')

    p_val_1_s1_list = p_val_csv['p_val_1_s1'].tolist()
    p_val_2_s1_list = p_val_csv['p_val_2_s1'].tolist()
    p_val_1_s2_list = p_val_csv['p_val_1_s2'].tolist()
    p_val_2_s2_list = p_val_csv['p_val_2_s2'].tolist()

    p_val_1_s1_adjusted = stats.p_adjust(FloatVector(p_val_1_s1_list), method=p_adj_method)
    p_val_2_s1_adjusted = stats.p_adjust(FloatVector(p_val_2_s1_list), method=p_adj_method)
    p_val_1_s2_adjusted = stats.p_adjust(FloatVector(p_val_1_s2_list), method=p_adj_method)
    p_val_2_s2_adjusted = stats.p_adjust(FloatVector(p_val_2_s2_list), method=p_adj_method)

    return p_val_1_s1_adjusted, p_val_2_s1_adjusted, p_val_1_s2_adjusted, p_val_2_s2_adjusted

def step_one(df, p1, p2, start_date, end_date):
    # Get the match results between player 1 and player 2
    historical_results = get_historical_results_list(p1, p2, df)[0]

    # Get the corresponding match dates for theese matches
    historical_results_date_list = get_historical_results_list(p1, p2, df)[1]

    # Get the number of runs
    num_runs = get_num_runs(historical_results)

    if num_runs == 1:
        return None, None, historical_results, historical_results_date_list, None, num_runs, None, None, None

    unique_historical_results_list = unique(historical_results)

    u1 = []
    u2 = []
    for u in historical_results:
        if u == unique_historical_results_list[0]:
            u1.append(u)
        elif u == unique_historical_results_list[1]:
            u2.append(u)

    n1 = len(u1)  # number of upset results
    n2 = len(u2)  # number of non-upsets
    n = n1 + n2  # total number of matches

    if WW_runs_test(num_runs, n1, n2, n) == None:
        wwz = None
    else:
        wwz = abs(WW_runs_test(num_runs, n1, n2, n))

    # calculate p-values
    if wwz is None:
        p_values_one = None
        p_values_two = None
    else:
        p_values_one = st.norm.sf(wwz)  # one-sided p-value
        p_values_two = st.norm.sf(wwz) * 2  # two-sided p-value

    return p_values_one, p_values_two, historical_results, historical_results_date_list, wwz, num_runs, n1, n2, n

def step_two(upset_results_list):   
    # Get the upset results between player 1 and player 2
    upset_results_list_unique = unique(upset_results_list)
    num_runs = get_num_runs(upset_results_list)
        
    u1 = []
    u2 = []
    for u in upset_results_list:
        if u == upset_results_list_unique[0]:
            u1.append(u)
        elif u == upset_results_list_unique[1]:
            u2.append(u)
    
    n_uw = len(u1)     # number of upset wins
    n_ul = len(u2)     # number of upset losses
    n_upsets = n_uw + n_ul      # total number of upsets
    
    p_values_one_s2 = None
    p_values_two_s2 = None
    ww_z = None
    
    # Run the Wald Wolfowitz runs test
    if num_runs > 1:
        ww_z = WW_runs_test(num_runs, n_uw, n_ul, n_upsets)
        if ww_z is not None:
            p_values_one_s2 = st.norm.sf(abs(ww_z))
            p_values_two_s2 = st.norm.sf(abs(ww_z)) * 2

    return upset_results_list, p_values_one_s2, p_values_two_s2, n_uw, n_ul, n_upsets, num_runs, ww_z

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

    header = ['player1', 'player2', 'results_set', 'upset_results_set', 'num_runs_s1', 'num_non_upset', 'num_upsets', 'num_matches', 'ww_z_s1', 'p_val_1_s1', 'p_val_2_s1', 'num_runs_s2', 'num_uw', 'num_ul', 'ww_z_s2', 'p_val_1_s2', 'p_val_2_s2', 'p_val_1_s1_adj', 'p_val_2_s1_adj', 'p_val_1_s2_adj', 'p_val_2_s2_adj']
    with open('bogey_results.csv', 'w', encoding='UTF8', newline='') as f:
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

            # Conduct step one - perform the WW runs test on the set of upset and non-upset results 
            p_value_one_s1, p_value_two_s1, historical_results, historical_results_date_list, ww_z_s1, num_runs_s1, n_non_upsets, n_upsets, n_matches = step_one(p1_p2_matches_df, p1, p2, start_date, end_date)
            
            # Considering only the upset results, get the set of upset types — upset wins and upset losses — between the two players
            upset_results = get_upset_result_list(p1, p2, p1_p2_matches_df)[0]
            upset_results_date_list = [date for date, result in zip(historical_results_date_list, historical_results) if result == 'U']

            ww_z_s2 = None
            
            # Check whether the p value from step one is significant
            if p_value_one_s1 == None:
                data = [str(p1), str(p2), list_of_tuples(historical_results_date_list, historical_results), list_of_tuples(upset_results_date_list, upset_results), num_runs_s1, n_non_upsets, n_upsets, n_matches, None, None, None, None, None, None, None, None, None, None]
            elif p_value_one_s1 < args.sig_level:
                # If it was significant, conduct step two
                upset_results, p_values_one_s2, p_values_two_s2, n_uw, n_ul, n_upsets, num_runs_s2, ww_z_s2 = step_two(upset_results)
                # Data to write out to the csv files
                data = [str(p1), str(p2), list_of_tuples(historical_results_date_list, historical_results), list_of_tuples(upset_results_date_list, upset_results), num_runs_s1, n_non_upsets, n_upsets, n_matches, ww_z_s1, p_value_one_s1, p_value_two_s1, num_runs_s2, n_uw, n_ul, n_upsets, ww_z_s2, p_values_one_s2, p_values_two_s2]
            else:
                if ww_z_s2 is not None:
                    ww_z_s2 = abs(ww_z_s2)
                # If it was not significant, don't conduct step two and leave the step two results blank
                data = [str(p1), str(p2), list_of_tuples(historical_results_date_list, historical_results), list_of_tuples(upset_results_date_list, upset_results), num_runs_s1, n_non_upsets, n_upsets, n_matches, ww_z_s1, p_value_one_s1, p_value_two_s1, None, None, None, None, None, None, None]

            writer.writerow(data)
            f.flush()

        # Read in the created bogey_results.csv file and create columns for the adjusted step one and step two p-values
        p_val_csv = pd.read_csv('bogey_results.csv')
        p_val_csv['p_val_1_s1_adj'] = 0.0
        p_val_csv['p_val_2_s1_adj'] = 0.0
        p_val_csv['p_val_1_s2_adj'] = 0.0
        p_val_csv['p_val_2_s2_adj'] = 0.0

        # Adjust the one- and two-sided p-values from steps one and two
        p_val_1_s1_adj, p_val_2_s1_adj, p_val_1_s2_adj, p_val_2_s2_adj = adjust_pvalues(p_val_csv, args.p_adj_method)

        # Set the adjusted p-values in the apprpriate df columns
        p_val_csv.iloc[:, -4] = p_val_1_s1_adj
        p_val_csv.iloc[:, -3] = p_val_2_s1_adj
        p_val_csv.iloc[:, -2] = p_val_1_s2_adj
        p_val_csv.iloc[:, -1] = p_val_2_s2_adj

        # Export the file with adjusted p-values to a csv
        p_val_csv.to_csv('bogey_results_adj.csv', index=False)

        # Also print results if only running for player pair
        if args.player_1 != 'all' and args.player_2 != 'all':
            print(str(p1) + ' vs. ' + str(p2))
            print('==== RESULTS ====')
            print('Results set (upset_results):')
            print(pd.DataFrame.from_records(list_of_tuples(upset_results_date_list, upset_results), columns=['Date', 'Result']).to_string(index=False))
            print()

if __name__ == '__main__':
    main()
