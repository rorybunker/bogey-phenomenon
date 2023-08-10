# Identification of Bogey Players in Tennis

This repository contains the code for the preprint Bunker, Yeung, and Fujii (2023), which is an expected wins approach that uses the Fisher’s exact test identify the bogey player effect in professional tennis.

The code for the previous conference paper (Bunker, 2022), which used a different approach with Wald-Walfowitz runs tests, is in the Archive folder.

## Dataset
Data_Clean_ATP_Elo_WElo.csv contains the ATP men's data including Elo ratings, and Data_Clean_WTA.csv contains the WTA women's data including Elo ratings.

These files were obtained Supplementary Data S1 in Appendix C. Supplementary materials, used by Angelini, Candila & De Angelis, 2022 (https://doi.org/10.1016/j.ejor.2021.04.011), and were passed through their clean() function in their welo R package (https://cran.r-project.org/web/packages/welo/index.html) before being exported to csv. This data was originally sourced by the authors from tennis-data.co.uk.

The csv file can be created by running the following create_data_clean_csv_files.R script (change to your own working directory first).

## Requirements & Environment
Create in conda using the following command
```
conda env create -f environment.yml
conda activate bogey
```

## Usage
```
python bogey_identification_fisher.py [--options]
```

## Options
| Argument        | Type    | Required | Default | Help                                                                                                    |
|-----------------|---------|----------|---------|---------------------------------------------------------------------------------------------------------|
| -p1, --player_1 | str     | False    | all     | Player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)  |
| -p2, --player_2 | str     | False    | all     | Player name in format Last Name Initial., enclosed in double quotes e.g., "Djokovic N." (default = all players)  |
| -d, --dataset   | str     | True     |         | atp or wta                                                                                              |
| -g, --grand_slam| int     | False    | 2       | 0 = non grand slams, 1 = grand slams only, 2 = grand slams and non grand slams (default)             |
| -t, --tournament| str     | False    | all     | Tournament name, e.g., Australian Open                                                                 |
| -s, --s_date    | str     | False    | min     | Start date in YYYY-MM-DD format (default = min date in dataset)                                       |
| -e, --e_date    | str     | False    | max     | End date in YYYY-MM-DD format (default = max date in dataset)                                         |
| -u, --upset     | str     | False    | odds    | Whether an unexpected result is based on the betting odds or elo rating (default=odds)                |

## References
Angelini, G., Candila, V., & De Angelis, L. (2022). Weighted Elo rating for tennis match predictions. European Journal of Operational Research, 297(1), 120-132. https://doi.org/10.1016/j.ejor.2021.04.011.

Bunker, R. (2022). The Bogey Phenomenon in Sport. In IX Mathsport International 2022 Proceedings.

Bunker, R.P., Yeung, C.C.K. and Fujii, K. (2023). An Expected Wins Approach Using Fisher’s Exact Test to Identify the Bogey Effect in Sports: An Application to Tennis. Preprint.
