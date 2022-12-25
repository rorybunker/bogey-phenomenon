# first, set your working directory to where your atp_2005_2020.RData and wta_2007_2020.RData files are downloaded to
setwd("/Users/rorybunker/Google Drive/Research/Tennis Prediction ML/Data/Vincenzo Data/WElo supplementary material/")
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