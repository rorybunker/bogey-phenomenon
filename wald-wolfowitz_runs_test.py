# Wald-Wolfowitz Runs Test (Actual)
# Adapted from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

import math
import scipy.stats as st # for pvalue 
import numpy as np
import bogey_player_identification_tennis

df_player1_player2 = bogey_player_identification_tennis.df_p1_p2
L = bogey_player_identification_tennis.get_hr_list(df_player1_player2)

# Finds runs in data: counts and creates a list of them
def getRuns(L):
  import itertools
  return len([sum(1 for _ in r) for _, r in itertools.groupby(L)])

# define the WW runs test described above
def WW_runs_test(R, n1, n2, n):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((2*n1*n2) * (2*n1*n2 - n)) / ((n**2)*(n-1)) )

    # compute the expected value of R if the null is true
    muR = ((2*n1*n2)/n) + 1

    # test statistic: R vs muR
    z = (R - muR) / seR

    return z

def unique(list1):
    x = np.array(list1)
    return list(np.unique(x))

# Gather info 
numRuns = getRuns(L) # Grab streaks in the data

L_unique = unique(L)

u1 = []
u2 = []
for u in L:
    if u == L_unique[0]:
        u1.append(u)
    elif u == L_unique[1]:
        u2.append(u)

# Define parameters
R = numRuns      # number of runs
n1 = len(u1)        # number of 'NOT UPSET'
n2 = len(u2)        # number of 'UPSET NOT WIN'
n = n1 + n2      # should equal len(L)

# Run the test
ww_z = WW_runs_test(R, n1, n2, n)

# test the pvalue
p_values_one = st.norm.sf(abs(ww_z))   #one-sided
p_values_two = st.norm.sf(abs(ww_z))*2 #twosided

# Print results
print('Wald-Wolfowitz Runs Test')
print('Number of runs: %s' %(R))
print('Number of 1\'s: %s; Number of 0\'s: %s ' %(n1,n2))
print('Z value: %s' %(ww_z))
print('One tailed P value: %s; Two tailed P value: %s ' %(p_values_one, p_values_two))

if p_values_one < 0.05:
    print(bogey_player_identification_tennis.get_ur_list(df_player1_player2))
