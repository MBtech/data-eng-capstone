import pandas as pd
import sys

inputfile = sys.argv[0]
outputfile = sys.argv[1]

dfs = pd.read_csv(inputfile, sep='\t', chunksize=50)
for df in dfs:
    df.to_csv(outputfile, sep=',', mode='a')