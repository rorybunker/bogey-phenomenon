import numpy as np
import matplotlib.pyplot as plt

# Data
# datasets = ['ATP', 'WTA', 'ATP Grand Slam', 'WTA Grand Slam', 'ATP Non grand slam', 'WTA Non grand slam']
# betting_odds = [0.02193, 0.04418, 0.01823, 0, 0.03813, 0.03739]
# elo_ratings = [0.09868, 0.08205, 0, 0, 0.07626, 0.05983]

datasets = ['ATP', 'WTA', 'ATP Grand Slam', 'WTA Grand Slam', 'ATP Non grand slam', 'WTA Non grand slam']
betting_odds = [0, 0.006312, 0, 0, 0, 0.007478]
elo_ratings = [0.0164, 0.0126, 0, 0, 0.0191, 0.015]

# Set width of bar
bar_width = 0.35

# Set position of bar on X axis
r1 = np.arange(len(datasets))
r2 = [x + bar_width for x in r1]

# Plotting
plt.figure(figsize=(10, 6))

bars1 = plt.bar(r1, betting_odds, color='blue', width=bar_width, edgecolor='grey', label='Betting Odds')
bars2 = plt.bar(r2, elo_ratings, color='orange', width=bar_width, edgecolor='grey', label='Elo Ratings')

plt.xlabel('Dataset', fontweight='bold')
plt.xticks([r + bar_width/2 for r in range(len(datasets))], datasets, rotation=45)
plt.ylabel('No. of bogey players identified as % of no. of player pairs in dataset', fontweight='bold')
plt.title('No. of bogey players identified by betting odds & elo ratings as a % of total no. of player pairs in dataset', fontweight='bold')
plt.legend()

# Set y-axis range
plt.ylim(0, 0.1)

# Add values on top of bars
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height, round(height, 5), ha='center', va='bottom')

for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height, round(height, 5), ha='center', va='bottom')

plt.tight_layout()
plt.show()
