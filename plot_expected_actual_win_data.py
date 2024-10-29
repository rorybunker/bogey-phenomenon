import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
import argparse
from matplotlib import rcParams

# Set global font to Times New Roman
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dataset', type=str, required=True, help='atp or wta')
parser.add_argument('-t', '--type', type=str, required=True, help='odds or elo')
parser.add_argument('-g', '--grand_slam', type=int, required=False, default=2, help='0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)')
args, _ = parser.parse_known_args()

if args.dataset == 'atp' and args.type == 'elo':
# Data preparation
    # ATP Elo
    data = {
        "player_pair": ["Garcia-Lopez G. vs Youzhny M.", "Baghdatis M. vs Garcia-Lopez G.", "Almagro N. vs Istomin D.", 
                        "Llodra M. vs Simon G.", "Gasquet R. vs Pouille L.", "Anderson K. vs Berdych T.", "Ancic M. vs Blake J.", 
                        "Acasuso J. vs Rochus C.", "Ramirez-Hidalgo R. vs Verdasco F.", "Nalbandian D. vs Verdasco F.", 
                        "Ginepri R. vs Korolev E.", "Kohlschreiber P. vs Mayer L.", "Berlocq C. vs Stakhovsky S.", 
                        "Benneteau J. vs Gulbis E.", "Fognini F. vs Paire B.", "Chardy J. vs Isner J.", 
                        "Querrey S. vs Ramos-Vinolas A.", "Isner J. vs Opelka R.", "Lorenzi P. vs Paire B."],
        "p_value": [0.0291, 0.0476, 0.0476, 0.0476, 0.0801, 0.0932, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        "expected_wins_diff": [3.20, 1.56, 2.12, 1.74, 2.08, 5.86, 1.18, 1.50, 1.30, 1.20, 1.32, 1.30, 1.02, 1.30, 1.02, 1.26, 1.34, 1.52, 1.14],
        "actual_wins_diff": [5, 5, 5, 5, 4, 12, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        "bogey_effect": ["Y", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"]
    }

if args.dataset == 'atp' and args.type == 'odds':
    # ATP Odds
    data = {
        "player_pair": ["Djokovic N. vs Monfils G.", "Ramirez-Hidalgo R. vs Verdasco F.", "Kohlschreiber P. vs Mayer L.",
                        "Benneteau J. vs Gulbis E.", "Goffin D. vs Pouille L."],
        "p_value": [0.0978, 0.1, 0.1, 0.1, 0.1],
        "expected_wins_diff": [7.94, 1.36, 1.22, 1.10, 1.32],
        "actual_wins_diff": [14.00, 3.00, 3.00, 3.00, 3.00],
        "bogey_effect": ["N", "Y", "Y", "Y", "Y"]
    }

if args.dataset == 'wta' and args.type == 'elo':
    # WTA Elo
    data = {
        "player_pair": [
            "Sharapova M. vs Williams S.", "Stosur S. vs Zvonareva V.", "Ivanovic A. vs Kuznetsova S.",
            "Stephens S. vs Voegele S.", "Petkovic A. vs Radwanska A.", "Goerges J. vs Stosur S.",
            "Chakvetadze A. vs Jankovic J.", "Safarova L. vs Shvedova Y.", "Hibino N. vs Stosur S.",
            "Date Krumm K. vs Kirilenko M.", "Cetkovska P. vs Radwanska A.", "Cetkovska P. vs Johansson M.",
            "Petkovic A. vs Rybarikova M.", "Pavlyuchenkova A. vs Wickmayer Y.", "Gavrilova D. vs Tsurenko L.",
            "Konta J. vs Strycova B."
        ],
        "p_value": [
            0.0184, 0.0256, 0.0325, 0.0476, 0.0769, 0.0801, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            5.88, 1.50, 1.14, 3.32, 1.76, 2.32, 1.26, 1.40, 1.82, 1.14, 2.20, 1.92, 1.18, 1.18, 1.04, 1.24
        ],
        "actual_wins_diff": [
            17, 8, 10, 3, 8, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "N", "Y", "N", "Y", "N", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "N", "Y"
        ]
    }

if args.dataset == 'wta' and args.type == 'odds':
    # WTA Odds
    data = {
        "player_pair": [
            "Sharapova M. vs Williams S.", "Stosur S. vs Zvonareva V.", "Ivanovic A. vs Kuznetsova S.",
            "Petkovic A. vs Radwanska A.", "Chakvetadze A. vs Jankovic J.", "Date Krumm K. vs Kirilenko M.",
            "Cetkovska P. vs Radwanska A.", "Cetkovska P. vs Johansson M.", "Riske A. vs Wang Q.",
            "Konta J. vs Strycova B."
        ],
        "p_value": [
            0.0184, 0.0256, 0.0325, 0.0769, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            6.20, 1.20, 1.30, 1.86, 1.16, 1.30, 1.92, 1.24, 1.02, 1.04
        ],
        "actual_wins_diff": [
            17, 8, 10, 8, 3, 3, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "N", "Y", "N", "N", "Y", "N", "Y", "Y", "N", "Y"
        ]
    }


if args.dataset == 'wta' and args.type == 'odds' and args.grand_slam == 0:
    # WTA Odds Non-Grand slam
    data = {
        "player_pair": [
            "Stosur S. vs Zvonareva V.", "Petkovic A. vs Radwanska A.", "Ivanovic A. vs Kuznetsova S.",
            "Sharapova M. vs Williams S.", "Chakvetadze A. vs Jankovic J.", "Date Krumm K. vs Kirilenko M.",
            "Ostapenko J. vs Wozniacki C.", "Riske A. vs Wang Q."
        ],
        "p_value": [
            0.021, 0.0769, 0.0824, 0.0867, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            1.06, 1.86, 1.58, 3.26, 1.16, 1.30, 1.10, 1.02
        ],
        "actual_wins_diff": [
            7, 8, 9, 10, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "Y", "N", "N", "N", "Y", "Y", "Y", "Y"
        ]
    }
if args.dataset == 'wta' and args.type == 'elo' and args.grand_slam == 0:
    # WTA Elo Non-Grand slam
    data = {
        "player_pair": [
            "Stosur S. vs Zvonareva V.", "Garcia C. vs Ivanovic A.", "Stephens S. vs Voegele S.",
            "Safarova L. vs Stosur S.", "Petkovic A. vs Radwanska A.", "Goerges J. vs Stosur S.",
            "Ivanovic A. vs Kuznetsova S.", "Sharapova M. vs Williams S.", "Chakvetadze A. vs Jankovic J.",
            "Hibino N. vs Stosur S.", "Date Krumm K. vs Kirilenko M.", "Ostapenko J. vs Wozniacki C.",
            "Petkovic A. vs Puig M."
        ],
        "p_value": [
            0.021, 0.0286, 0.0476, 0.0698, 0.0769, 0.0801, 0.0824, 0.0867, 0.1, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            1.34, 2.08, 3.32, 2.66, 1.76, 2.32, 1.20, 2.74, 1.26, 1.82, 1.14, 1.66, 1.32
        ],
        "actual_wins_diff": [
            7, 4, 3, 6, 8, 4, 9, 10, 3, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "Y", "Y", "N", "Y", "N", "Y", "N", "N", "Y", "Y", "N", "Y", "Y"
        ]
    }

if args.dataset == 'atp' and args.type == 'elo' and args.grand_slam == 0:
    # ATP Elo Non-Grand slam
    data = {
        "player_pair": [
            "Garcia-Lopez G. vs Youzhny M.", "Baghdatis M. vs Garcia-Lopez G.", "Llodra M. vs Simon G.",
            "Almagro N. vs Robredo T.", "Ancic M. vs Blake J.", "Acasuso J. vs Rochus C.",
            "Ramirez-Hidalgo R. vs Verdasco F.", "Benneteau J. vs Wawrinka S.", "Ginepri R. vs Korolev E.",
            "Almagro N. vs Istomin D.", "Gulbis E. vs Stepanek R.", "Kohlschreiber P. vs Sijsling I.",
            "Benneteau J. vs Gulbis E.", "Querrey S. vs Ramos-Vinolas A.", "Lorenzi P. vs Paire B."
        ],
        "p_value": [
            0.0291, 0.0476, 0.0476, 0.0769, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            3.20, 1.56, 1.74, 0.94, 1.18, 1.50, 1.30, 1.50, 1.32, 1.22, 1.36, 1.56, 1.30, 1.34, 1.14
        ],
        "actual_wins_diff": [
            5, 5, 5, 8, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "Y", "Y", "Y", "N", "Y", "N", "Y", "Y", "Y", "Y", "Y", "Y", "N", "Y", "Y"
        ]
    }


if args.dataset == 'atp' and args.type == 'odds' and args.grand_slam == 0:
    # ATP Odds Non-Grand slam
    data = {
        "player_pair": [
            "Almagro N. vs Robredo T.", "Ramirez-Hidalgo R. vs Verdasco F.", "Benneteau J. vs Wawrinka S.",
            "Davydenko N. vs Kiefer N.", "Kohlschreiber P. vs Sijsling I.", "Benneteau J. vs Gulbis E.",
            "Goffin D. vs Pouille L."
        ],
        "p_value": [
            0.0769, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1
        ],
        "expected_wins_diff": [
            1.92, 1.36, 1.28, 1.12, 1.18, 1.10, 1.32
        ],
        "actual_wins_diff": [
            8, 3, 3, 3, 3, 3, 3
        ],
        "bogey_effect": [
            "N", "Y", "Y", "Y", "Y", "Y", "Y"
        ]
    }

df = pd.DataFrame(data)

# Separate data based on bogey effect
df_bogey = df[df['bogey_effect'] == 'Y']
df_non_bogey = df[df['bogey_effect'] == 'N']

# Assign unique colors to each player pair
unique_colors = plt.cm.tab20(np.linspace(0, 1, len(df)))

# Normalize p_value for point sizes
min_size, max_size = 10, 100  # Reduced the sizes
sizes = min_size + (df['p_value'] - df['p_value'].min()) / (df['p_value'].max() - df['p_value'].min()) * (max_size - min_size)

# Plotting
fig, ax = plt.subplots()

# Scatter plot for bogey effect 'Y'
sc_bogey = ax.scatter(df_bogey['expected_wins_diff'], df_bogey['actual_wins_diff'], c=unique_colors[df_bogey.index], s=sizes[df_bogey.index], marker='o', label='Bogey Effect = Y')

# Scatter plot for bogey effect 'N'
sc_non_bogey = ax.scatter(df_non_bogey['expected_wins_diff'], df_non_bogey['actual_wins_diff'], c=unique_colors[df_non_bogey.index], s=sizes[df_non_bogey.index], marker='s', label='Bogey Effect = N')

# Custom legend for player pairs
lines = [Line2D([0], [0], marker='o', color='w', markerfacecolor=unique_colors[i], markersize=10) for i in range(len(df))]
labels = df['player_pair'].tolist()

# Add custom legend for player pairs
legend2 = ax.legend(lines, labels, loc='center left', title='Player Pair', bbox_to_anchor=(1, 0.5), fontsize='small')
ax.add_artist(legend2)

# Custom legend for p-value sizes
size_legend = [Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=np.sqrt(size)) for size in [min_size, (min_size + max_size) / 2, max_size]]
size_labels = [f'{"%.4f" % df["p_value"].min()}', f'{"%.4f" % ((df["p_value"].min() + df["p_value"].max()) / 2)}', f'{"%.4f" % df["p_value"].max()}']
legend1 = ax.legend(size_legend, size_labels, loc='upper left', title='p-value (size)')
ax.add_artist(legend1)

# Add legend for bogey effect without color
legend_elements = [Line2D([0], [0], marker='o', color='black', markerfacecolor='none', markersize=10, label='Bogey Effect = Y'),
                   Line2D([0], [0], marker='s', color='black', markerfacecolor='none', markersize=10, label='Bogey Effect = N')]
legend3 = ax.legend(handles=legend_elements, loc='lower right', title='Bogey Effect')
ax.add_artist(legend3)

# Set the aspect ratio of the plot to be equal
ax.set_aspect('equal', adjustable='datalim')

# Set the same range for both axes with a buffer
all_data = np.concatenate([df['expected_wins_diff'], df['actual_wins_diff']])
data_min, data_max = all_data.min(), all_data.max()
data_range = data_max - data_min
buffer = data_range * 0.2  # 20% buffer
ax.set_xlim(data_min - buffer, data_max + buffer)
ax.set_ylim(data_min - buffer, data_max + buffer)

ax.set_xlabel('Expected Wins Difference')
ax.set_ylabel('Actual Wins Difference')
# ax.set_title('Expected vs Actual Wins Difference with p-value Size Scale')

# Adjust layout to make room for the legends
fig.tight_layout(rect=[0, 0, 0.75, 1])  # Adjust rect to make room for legends

# Show plot
plt.show()