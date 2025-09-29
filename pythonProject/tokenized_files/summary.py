import pandas
import csv
import os

EXCEL_FILES = ["administrative_texts", "newspapers"]
FOLDER = "tokenized_files"

def to_connlu():
    for file in EXCEL_FILES:
        df = pandas.read_excel(os.path.join(FOLDER, file + ".xlsx"), header=None)
        df.to_csv(file + ".conllu", sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')
        print("Konvertovan "+ file)


CONLLU_FILES = ["administrative_texts", "newspapers", "twitter", "literature"]


def summerize():
    
    rows = []
    for file in CONLLU_FILES:
        annotations = {
            "O" : 0, 
            "I-PER" : 0, 
            "B-PER" : 0, 
            "I-ORG" : 0, 
            "B-ORG" : 0, 
            "I-LOC" : 0, 
            "B-LOC" : 0
        }
        with open(os.path.join(FOLDER, file + ".conllu"), "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip() 
                if not line or line.startswith("#"):
                    continue

                cols = line.split("\t")
                if len(cols) < 11:
                    print(f"Greska u fajlu {file} na liniji {line_number}: Nedostaje anotacija.")
                    continue

                token = cols[1]
                annotation = cols[10]

                if annotation not in annotations:
                    print(f"Greska u fajlu {file} na liniji {line_number}: {token} = {annotation}")
                else:
                    annotations[annotation] += 1

        print(f"{file}")
        for a, val in annotations.items():
            print(f"{a}: {val}")
        per = annotations['B-PER'] + annotations['I-PER']
        org = annotations['B-ORG'] + annotations['I-ORG']
        loc = annotations['B-LOC'] + annotations['I-LOC']
        print(f"Ukupno PER: {per}")
        print(f"Ukupno ORG: {org}")
        print(f"Ukupno LOC: {loc}")
        entities = sum(val for a in annotations.items() if a != "O")
        all = entities + annotations["O"]
        print(f"Ukupno entiteta: {entities}")
        print(f"Ukupno tokena: {all}\n")
        rows.append([file, annotations["O"], annotations["I-PER"], annotations["B-PER"],annotations["I-ORG"], annotations["B-ORG"], annotations["I-LOC"], annotations["B-LOC"], per, org, loc, entities, all])
        

    df = pandas.DataFrame(rows, columns=["domen", "O", "I-PER", "B-PER", "I-ORG", "B-ORG",  "I-LOC", "B-LOC", "PER", "ORG", "LOC", "ukupno NE", "ukupno tokena"]) 
    df.to_excel(os.path.join(FOLDER, "summary.xlsx"), header=True, index=False)
        

# to_connlu()
summerize()