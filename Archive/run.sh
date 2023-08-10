#!/bin/bash
# load virtual environment
source ${HOME}/workspace2/virtualenvs/venv/bin/activate bogey
# execute python script
startDateArray=(2006-01-01 2007-01-01)
endDateArray=(2006-12-31 2007-12-31)

for S in ${startDateArray[@]}; do
    for E in ${endDateArray[@]}; do
        for T in 'Australian Open' 'US Open' 'French Open' 'Wimbledon'; do
            for D in atp wta; do
                for Z in std cc; do
                    echo --------------------------
                    echo Iteration $iter. Parameters: start date $S, end date $E, tournament $T, dataset $D, z-statistic $Z...              
                    python -u bogey_identification_tennis_v3.py -d $D -t $T -s $S -e $E -z $Z   
                    dt=$(date '+%d/%m/%Y %H:%M:%S');
                    echo "$dt"
                    ((iter++))
                done
            done
        done
    done
done