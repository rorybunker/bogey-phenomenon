import pandas as pd
import matplotlib.pyplot as plt

# Define the dataset
data = {
    'Dataset': ['ATP Elo', 'ATP Elo', 'ATP Odds', 'ATP Odds', 'ATP Elo Grandslam', 'ATP Elo Grandslam', 'ATP Elo Non-Grand slam', 'ATP Elo Non-Grand slam',
                'ATP Odds Grandslam', 'ATP Odds Grandslam', 'ATP Odds Non-Grand slam', 'ATP Odds Non-Grand slam', 'WTA Elo', 'WTA Elo', 'WTA Odds', 'WTA Odds',
                'WTA Elo Grandslam', 'WTA Elo Grandslam', 'WTA Elo Non-Grand slam', 'WTA Elo Non-Grand slam', 'WTA Odds Grandslam', 'WTA Odds Grandslam',
                'WTA Odds Non-Grand slam', 'WTA Odds Non-Grand slam'],
    'Player pair type': ['Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player',
                         'Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player',
                         'Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player',
                         'Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player',
                         'Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player',
                         'Pair w/o bogey player', 'Pair w/ bogey player', 'Pair w/o bogey player', 'Pair w/ bogey player'],
    'Average Expected Win': [0.6952, 0.704, 0.6787, 0.708, 0.7333, '-', 0.6886, 0.715, 0.7358, 0.6904, 0.6676, 0.7041, 0.6887, 0.7322, 0.6722, 0.6929,
                             0.7244, '-', 0.6807, 0.7217, 0.7133, '-', 0.6626, 0.6677],
    'Average Actual wins': [0.6665, 0.0172, 0.7034, 0, 0.7329, '-', 0.6497, 0.0102, 0.7741, 0, 0.6841, 0, 0.6592, 0.0282, 0.6925, 0, 0.7043, '-', 0.6475, 0.0567,
                            0.7331, '-', 0.6814, 0],
    'Average difference in Expected and Actual wins': [-0.0073, 0.6868, -0.0247, 0.708, 0.00044, '-', 0.0389, 0.7048, -0.0382, 0.6904, -0.0166, 0.7041,
                                                       0.0295, 0.704, -0.0203, 0.6929, 0.02, '-', 0.0331, 0.665, -0.0198, '-', -0.0188, 0.6677]
}

# Create DataFrame
df = pd.DataFrame(data)

# Remove rows with missing values ('-')
df = df.replace('-', pd.NA)
df = df.dropna()

# Convert columns to numeric
df[['Average Expected Win', 'Average Actual wins', 'Average difference in Expected and Actual wins']] = df[
    ['Average Expected Win', 'Average Actual wins', 'Average difference in Expected and Actual wins']].apply(pd.to_numeric)

# Sort DataFrame by 'Dataset' column
df = df.sort_values(by='Dataset')

# Plot
plt.figure(figsize=(12, 8))

for pair_type, group in df.groupby('Player pair type'):
    actual_wins = group['Average Actual wins']
    expected_wins = group['Average Expected Win']
    
    plt.scatter(group['Dataset'], actual_wins, label=f'{pair_type} - Actual Wins')
    plt.scatter(group['Dataset'], expected_wins, label=f'{pair_type} - Expected Wins', marker='x')
    # Plotting the difference as line segments
    for i in range(len(group)):
        plt.plot([group['Dataset'].iloc[i], group['Dataset'].iloc[i]], [actual_wins.iloc[i], expected_wins.iloc[i]], color='gray', linestyle='--')
        # Shifting annotations to the right slightly
        shift = 0.1 # adjust this value to shift more or less
        if pair_type == 'Pair w/o bogey player':
            color = 'red'
        else:
            color = 'blue'
        plt.text(group['Dataset'].iloc[i], (actual_wins.iloc[i] + expected_wins.iloc[i]) / 2, 
                 f"{group['Average difference in Expected and Actual wins'].iloc[i]:.4f}", 
                 color=color, ha='left', va='center', fontsize=8)

plt.xticks(rotation=90)
plt.legend()
# plt.title('Performance Metrics by Dataset and Player Pair Type')
# plt.ylabel('Average Wins')
plt.xlabel('Dataset')
plt.tight_layout()
plt.savefig('avg_expected_win_plot.png')



