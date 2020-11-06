#!/bin/bash
mkdir -p data
cd data

for i in $(seq -w 01 31);
do

wget https://github.com/thepanacealab/covid19_twitter/raw/master/dailies/2020-10-${i}/2020-10-${i}_clean-dataset.tsv.gz


done


