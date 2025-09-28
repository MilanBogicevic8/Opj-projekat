import pandas
import csv

EXCEL_FILES = ["milan", "milica"] #aleksa

def to_connlu():
    for file in EXCEL_FILES:
        df = pandas.read_excel("literature-" + file + ".xlsx", header=None)
        df = df.head(4015)
        df.to_csv("literature-" + file + "-annotations.conllu", sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')
        print("Konvertovan "+ file)




CONLLU_FILES = ["milan", "milica", "aleksa"] 

def calibrate():
    print("Samo u kalibraciji tretiramo ćirilično i latinično O jednako.")
    all_files = [open("literature-" + f + "-annotations.conllu", "r", encoding="utf-8") for f in CONLLU_FILES]
    for line_number, lines in enumerate(zip(*all_files), start=1):
        lines = [line.strip() for line in lines]
        if all(not line or line.startswith("#") for line in lines):
            continue
        elif any(not line or line.startswith("#") for line in lines):
            print(f"Napomena u liniji {line_number}: Prazne linije ili komentari se ne poklapaju.")
            continue
        
        cols = [line.split("\t") for line in lines]

        if any(len(c) < 2 for c in cols):
            print(f"Greska u na liniji {line_number} - u jednom od fajlova nedostaje token zajedno sa ostatkom linije.")
            print("Prekinuto izvrsavanje")
            return
        
        tokens = set(c[1] for c in cols)
        if len(tokens) != 1:
            print(f"Greska u na liniji {line_number} - tokeni se razlikuju: {tokens}")
            print("Prekinuto izvrsavanje")
            return
        
        if any(len(c) < 11 for c in cols):
            annotations = set(c[10] for c in cols if len(c) == 11)
            print(f"Greska u na liniji {line_number} - u jednom od fajlova nedostaje anotacija. Prostale su {annotations}.")
            continue

        
            
        # konverzija ćiriličnog O u  latinično
        for c in cols:
            if c[10] == "О":
                c[10] = "O" 
        
        annotations_list = [c[10] for c in cols]
        annotations = set(annotations_list)
        if len(annotations) != 1:
            print(f"Greska u na liniji {line_number} - anotacije za token {tokens} se razlikuju: {annotations} - većinska odluka: {max(annotations_list, key=annotations_list.count)}")
            continue
    for f in all_files:
        f.close()


to_connlu()
calibrate()