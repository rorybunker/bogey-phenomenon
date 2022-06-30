# Bogey Players in Sport

The Wald-Wolfowitz test is adapted from code from https://gist.github.com/kwcooper/b1ff695d6ff9dc0189d52fe9ba4dc567

Tennis data: Same data used by Angelini, Candila & De Angelis (2021) https://bit.ly/3EwY9vo, originally sourced from
http://www.tennis-data.co.uk/

## Parameters
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

![image](https://user-images.githubusercontent.com/29388472/166176166-2a2ed1bc-61b6-4fdc-a102-89dd91f1f4a3.png)
