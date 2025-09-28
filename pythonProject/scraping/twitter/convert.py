import pandas
from scraping.twitter.const import *
import csv

def excel_to_conllu(input: Path, output: Path):
    df = pandas.read_excel(input, header=None)
    for i, row in df.iterrows():
        if not pandas.isna(row[0]) and not str(row[0]).startswith("#") and pandas.isna(row[10]): 
            row[10] = "O"
    df.to_csv(output, sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE)

def conllu_to_excel(input: Path, output: Path):
    table = [it.split("\t") if not it.startswith("#") and not len(it) == 0 else [it] for it in input.read_text().split("\n")]
    df = pandas.DataFrame(table)
    df.to_excel(output, index=False, header=False)

def merge_conllu(inputs: list[Path], output: Path):
    output.write_text("\n".join(it.read_text() for it in inputs))

