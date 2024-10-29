import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set global font to Times New Roman
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']

# Data 95% confidence
datasets = ['ATP', 'WTA', 'ATP Grand Slam', 'WTA Grand Slam', 'ATP Non grand slam', 'WTA Non grand slam']
betting_odds = [0, 0.006312, 0, 0, 0, 0.007478]
elo_ratings = [0.0164, 0.0126, 0, 0, 0.0191, 0.015]

# Data 90% confidence
# datasets = ['ATP', 'WTA', 'ATP Grand Slam', 'WTA Grand Slam', 'ATP Non grand slam', 'WTA Non grand slam']
# betting_odds = [0.02193, 0.04418, 0.01823, 0, 0.03813, 0.03739]
# elo_ratings = [0.09868, 0.08205, 0, 0, 0.07626, 0.05983]

# Set width of bar
bar_width = 0.35

# Set position of bar on X axis
r1 = np.arange(len(datasets))
r2 = [x + bar_width for x in r1]

# Plotting
plt.figure(figsize=(12, 8))

bars1 = plt.bar(r1, betting_odds, color='blue', width=bar_width, edgecolor='grey', label='Betting Odds')
bars2 = plt.bar(r2, elo_ratings, color='orange', width=bar_width, edgecolor='grey', label='Elo Ratings')

# Set axis labels and title with increased font size
plt.xlabel('Dataset', fontsize=20, fontweight='bold')

# Set x-ticks with increased font size
plt.xticks([r + bar_width/2 for r in range(len(datasets))], datasets, rotation=45, fontsize=20)

# Set y-ticks with increased font size
plt.yticks(fontsize=20)

# Add legend with increased font size and remove border
legend = plt.legend(fontsize=20, loc='upper right')
legend.get_frame().set_visible(False)  # Remove border from the legend

# Set y-axis range
plt.ylim(0, 0.1)

# Remove top and right borders
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

# Add values on top of bars with increased font size
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height, round(height, 5), ha='center', va='bottom', fontsize=20)

for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height, round(height, 5), ha='center', va='bottom', fontsize=20)

plt.tight_layout()
plt.show()
