# Identification of Bogey Players in Tennis

## Dataset
Data_Clean.csv is the same ATP men's data used by Angelini, Candila & De Angelis, 2022 (https://doi.org/10.1016/j.ejor.2021.04.011), passed through their clean() function in their welo R package (https://cran.r-project.org/web/packages/welo/index.html).

```
# first, set your working directory to where your atp_2005_2020.RData and wta_2007_2020.RData files are downloaded to
setwd("...")
# install welo package if it is not already installed
list.of.packages <- c("welo")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
# load the welo library
library("welo")
# load the .RData file
load("atp_2005_2020.RData")
# apply the welo package's clean function to the loaded data
db_clean <- clean(db)
# output the cleaned dataset to a csv file
write.csv(db_clean,"Data_Clean.csv", row.names = FALSE)
```
```

## Requirements & Environment
A python 3 environment with pandas and scipy installed, e.g.,
```
% conda create --name bogey
% conda activate bogey
% conda install pandas
% conda install scipy
```

## Usage & Options
```
% python3 bogey_identification_tennis_v3.py -h
```
```
usage: bogey_identification_tennis_v3.py [-h] [-a PLAYER_1] [-b PLAYER_2]
                                         [-g GRAND_SLAM] [-t TOURNAMENT]
                                         [-s S_DATE] [-e E_DATE]
                                         [-z Z_VAL_TYPE]

options:
  -h, --help            show this help message and exit
  -a PLAYER_1, --player_1 PLAYER_1
                        player name in format Last Name, Initial., enclosed in
                        double quotes e.g., "Djokovic, N." (default = all
                        players)
  -b PLAYER_2, --player_2 PLAYER_2
                        player name in format Last Name, Initial., enclosed in
                        double quotes e.g., "Djokovic, N." (default = all
                        players)
  -g GRAND_SLAM, --grand_slam GRAND_SLAM
                        0 = non grand slams, 1 = grand slams only, 2 = grand
                        slams and non grand slams (default)
  -t TOURNAMENT, --tournament TOURNAMENT
                        tournament name, e.g., Australian Open
  -s S_DATE, --s_date S_DATE
                        start date in YYYY-MM-DD format (default = min date in
                        dataset)
  -e E_DATE, --e_date E_DATE
                        end date in YYYY-MM-DD format (default = max date in
                        dataset)
  -z Z_VAL_TYPE, --z_val_type Z_VAL_TYPE
                        type of z statistic - standard std or continuity
                        corrected cc (default = cc)
```
## References
Angelini, G., Candila, V., & De Angelis, L. (2022). Weighted Elo rating for tennis match predictions. European Journal of Operational Research, 297(1), 120-132. https://doi.org/10.1016/j.ejor.2021.04.011.
