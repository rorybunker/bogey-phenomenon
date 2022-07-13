# Bogey Players in Sport

The Wald-Wolfowitz test is adapted from code from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

Tennis data: Same data used by Angelini, Candila & De Angelis (2021) https://bit.ly/3EwY9vo, originally sourced from
http://www.tennis-data.co.uk/

## Usage
### bogey_identification_tennis.py
- specify the two players in p1 and p2 in Last Name First Initial format, e.g., p1 = 'Murray A.' p2 = 'Djokovic N.'
- uncomment this line if you want to run for a specific tournament, e.g, for the Australian Open only:
df = df[(df["Tournament"] == "Australian Open")]
- uncomment this line if you want to run for Grand Slams only:
df = df[(df["Series"] == "Grand Slam")]
- uncomment this line if you want to run for non-Grand Slam tournaments only:
df = df[(df["Series"] != "Grand Slam")]
- specify dates (start_date and end_date) in the format "YYYY-MM-DD" if you want to check for a specific date range, or use start_date = min(df["Date"]) and end_date = max(df["Date"]) for entire dataset's date range:
- specify the statistical significance level in sig_level, e.g., for 95% level/alpha = 0.05:
sig_level = 0.05

![Fig1_Method_Flow_v2](https://user-images.githubusercontent.com/29388472/177063908-f673b1e8-7d37-4c6b-9e80-c3267eb5b5e0.jpg)

## Example Output
### bogey_identification_tennis.py
p1 = 'Ferrer D.', 
p2 = 'Lopez F.', 
sig_level = 0.05
```
Ferrer D. vs. Lopez F.
==== STEP 1 RESULTS ====
Historical results set (HR):
      Date Result
2005-08-27      U
2006-10-12      U
2007-10-05      N
2007-10-17      U
2008-03-06      U
2008-10-15      U
2009-04-14      N
2011-04-13      N
2011-10-15      N
2012-04-27      N
2013-05-31      N
2014-02-27      N
2015-10-04      N
2016-05-28      N
2016-10-11      U
2017-06-01      U

Wald-Wolfowitz Runs Test
Number of runs: 5
Number of Ns: 9; Number of Us: 7 
Z value: -2.039650254375284
One tailed P value: 0.020692586443467945; Two tailed P value: 0.04138517288693589 

==== STEP 2 RESULTS ====
Upset results set (UR):
      Date Result
2005-08-27     UL
2006-10-12     UL
2007-10-05     UL
2007-10-17     UL
2008-03-06     UL
2008-10-15     UL
2009-04-14     UL

Number of UWs: 0
Number of ULs: 7
0.0% of upset results were UWs
100.0% of upset results were ULs
0.0% of matches were UWs
43.75% of matches were ULs
```

## Example Output
### bogey_identification_tennis_v2.py
p1 = 'Ferrer D.', 
p2 = 'Lopez F.'
```
Ferrer D. vs. Lopez F.
==== RESULTS ====
Results set (RS):
      Date Result
2005-08-27     UL
2006-10-12     UL
2007-10-05      N
2007-10-17     UL
2008-03-06     UL
2008-10-15     UL
2009-04-14      N
2011-04-13      N
2011-10-15      N
2012-04-27      N
2013-05-31      N
2014-02-27      N
2015-10-04      N
2016-05-28      N
2016-10-11     UL
2017-06-01     UL

Wald-Wolfowitz Runs Test
Number of runs: 5
Number of Ns: 9; Number of ULs: 7; Number of UWs: 0 
Z value: -1.7764695763913763
One tailed P value: 0.037827776066450346; Two tailed P value: 0.07565555213290069 
```
