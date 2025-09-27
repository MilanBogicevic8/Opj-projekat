import pandas
from scraping.twitter.const import *
import csv

df = pandas.read_excel(ANNOTATIONS_EXCEL, header=None)
for i, row in df.iterrows():
    if not pandas.isna(row[0]) and not row[0].startswith("#") and pandas.isna(row[10]): 
        row[10] = "O"
df.to_csv(ANNOTATIONS_CONLLU, sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE)
