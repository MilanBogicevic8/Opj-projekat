import pandas
from scraping.twitter.const import *
import csv
import unicodedata

translit_map = {
    'č': 'c', 'ć': 'c', 'đ': 'dj', 'š': 's', 'ž': 'z',
    'Č': 'C', 'Ć': 'C', 'Đ': 'Dj', 'Š': 'S', 'Ž': 'Z'
}
def normalize(text) -> str:
    text = unicodedata.normalize('NFC', text)
    return ''.join([translit_map.get(c) or c for c in text])

def excel_to_conllu(input: Path, output: Path):
    df = pandas.read_excel(input, header=None)
    for i, row in df.iterrows():
        if not pandas.isna(row[0]) and not str(row[0]).startswith("#") and pandas.isna(row[10]): 
            row[10] = "O"
    df.to_csv(output, sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE)

def conllu_to_excel(input: Path, output: Path):
    table = [it.split("\t") if not it.startswith("#") and not len(it.strip()) == 0 else [it] for it in input.read_text().split("\n")]
    df = pandas.DataFrame(table)
    df.to_excel(output, index=False, header=False)

def merge_conllu(inputs: list[Path], output: Path):
    output.write_text("\n".join(it.read_text() for it in inputs))

def copy_conllu(input: Path, output: Path):
    left = input.read_text().split("\n")
    right = output.read_text().split("\n")
    def next(lines: list[str], i: int) -> int|None:
        while i < len(lines) and (not len(lines[i].strip()) or lines[i].startswith("#")): i += 1
        return i if i < len(lines) else None
    
    x, y = 0, 0
    while True:
        x, y = next(left, x), next(right, y)
        if x is None or y is None: break
        left_cells = left[x].split("\t")
        right_cells = right[y].split("\t")
        left_token = left_cells[1]
        right_token = right_cells[1]
        if normalize(left_token) != normalize(right_token):
            if left_token == "" and right_token == "NA":
                left_token = right_token
            elif right_token in {';', '́'}:
                print(f"Skipping mismatch {left_token} {right_token}")
                y += 1
                continue
            else:
                raise Exception(f"Token mismatch: '{left_token}' != '{right_token}'.\nInput line {x}: {left[x]}\nOutput line {y}: {right[y]}")
        if len(left_cells) < 11: left_tag = "O"
        else: left_tag = left_cells[-1] or "O"
        if len(right_cells) < 10: raise Exception("")
        if len(right_cells) == 10: right_cells.append(left_tag)
        else: right_cells[10] = left_tag
        right[y] = "\t".join(right_cells)
        x += 1
        y += 1
    if x is None != y is None:
        raise Exception("Unexpected end of file")
        
    
    output.write_text("\n".join(right))
    print("SUCCESS")

