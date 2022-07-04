#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
k-Category Extension of the Single-Sample Runs Test for Randomness (with k = 3)
https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/NCSS/Analysis_of_Runs.pdf
pages: 256-6/256-7
@author: rorybunker
"""
import math

L = [1, 0, 1, 1, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2]

def getRuns(L):
  import itertools
  
  return len([sum(1 for _ in r) for _, r in itertools.groupby(L)])

def WW_runs_test_k_3(R, n1, n2, n3, n):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((n1**2 + n2**2 + n3**2)*((n1**2 + n2**2 + n3**2) + n*(n+1)) - 2*n*(n1**3 + n2**3 + n3**3) - n**3)/(n**2*(n - 1)) ) 
    # compute the expected value of R if the null is true
    muR = (n*(n+1) - (n1**2 + n2**2 + n3**2))/n
                   
    # asymptotic standard normal z statistic
    z = (R - muR) / seR
    
    # asymptotic continuity-corrected standard normal z statistic
    if R >= muR: 
        z_cc = (R - muR - 0.5)/seR
    elif R < muR:
        z_cc = (R - muR + 0.5)/seR

    return z, z_cc

def WW_runs_test(R, n1, n2, n):
    # compute the standard error of R if the null (random) is true
    seR = math.sqrt( ((2*n1*n2) * (2*n1*n2 - n)) / ((n**2)*(n-1)) )

    # compute the expected value of R if the null is true
    muR = ((2*n1*n2)/n) + 1

    # test statistic: R vs muR
    z = (R - muR) / seR

    return z

R = getRuns(L)      # number of runs
n2 = 0
for l in L:
    if l == 2:
        n2 += 1
n1 = 0
for l in L:
    if l == 1:
        n1 += 1
n0 = 0  
for l in L:
    if l == 0:
        n0 += 1 
        
n = n0 + n1 + n2     # should equal len(L)

print(WW_runs_test_k_3(R, n0, n1, n2, n)[1])
print(WW_runs_test_k_3(R, n0, n1, n2, n)[0])
print(WW_runs_test(R, n0, n1, n))
