# Identification of Bogey Players in Tennis

## Dataset
Data_Clean.csv is the ATP men's data, Supplementary Data S1 in Appendix C. Supplementary materials, used by Angelini, Candila & De Angelis, 2022 (https://doi.org/10.1016/j.ejor.2021.04.011), passed through their clean() function in their welo R package (https://cran.r-project.org/web/packages/welo/index.html). This data was originally sourced by the authors from tennis-data.co.uk.

The csv file can be created by running the following create_data_clean_csv_files.R script.

## Requirements & Environment
A python 3 environment with pandas and scipy installed, e.g.,
```
conda create --name bogey
conda activate bogey
conda install pandas
conda install scipy
```

## Usage
```
python bogey_identification_tennis_v3.py [--options]
```
## Options
-a/--player1: Player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)\
-b/--player2: Player name in format Last Name, Initial., enclosed in double quotes e.g., "Djokovic, N." (default = all players)\
-d/--dataset: atp (mens), wta (womens), or test\
-g/--grandslam: 0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)\
-t/--tournament: Tournament name, e.g., Australian Open (default is all tournaments)\
-s/--s_date: Start date in YYYY-MM-DD format (default = min date in dataset)\
-e/--e_date: End date in YYYY-MM-DD format (default = max date in dataset)\
-z/--z_val_type: Type of z statistic - standard std or continuity corrected cc (default = cc)\
-p/--p_adj_method: P-value adjustment for multiple comparisons method, e.g., bonferroni, hochberg, BH, holm, hommel, BY. Default is BH.

## References
Angelini, G., Candila, V., & De Angelis, L. (2022). Weighted Elo rating for tennis match predictions. European Journal of Operational Research, 297(1), 120-132. https://doi.org/10.1016/j.ejor.2021.04.011.
