import pandas
import csv

EXCEL_FILES = ["administrative_texts", "newspapers"]

def to_connlu():
    for file in EXCEL_FILES:
        df = pandas.read_excel(file + ".xlsx", header=None)
        df.to_csv(file + ".conllu", sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')
        print("Konvertovan "+ file)

to_connlu()


CONLLU_FILES = ["administrative_texts", "newspapers", "twitter", "literature"]

def summerize():
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

        with open(file + ".conllu", "r", encoding="utf-8") as f:
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
        print(f"Ukupno ORG: {annotations['B-ORG'] + annotations['I-ORG']}")
        print(f"Ukupno LOC: {annotations['B-LOC'] + annotations['I-LOC']}")
        print(f"Ukupno PER: {annotations['B-PER'] + annotations['I-PER']}")
        entities = sum(val for a in annotations.items() if a != "O")
        print(f"Ukupno entiteta: {entities}")
        print(f"Ukupno tokena: {entities + annotations["O"]}\n")


summerize()