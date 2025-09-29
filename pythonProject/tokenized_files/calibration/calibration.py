import pandas
import csv
import os

EXCEL_FILES = ["milan", "milica", "aleksa"]
FOLDER = os.path.join("tokenized_files", "calibration")

def to_connlu():
    for file in EXCEL_FILES:
        df = pandas.read_excel(os.path.join(FOLDER, "literature-" + file + ".xlsx"), header=None)
        df = df.head(4015)
        df.to_csv("literature-" + file + "-annotations.conllu", sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\')
        print("Konvertovan "+ file)




CONLLU_FILES = ["milan", "milica", "aleksa"] 

binary = {
    "milan-milica": [],
    "milan-aleksa" : [],
    "milica-aleksa" : []
}

def calibrate():
    print("Samo u kalibraciji tretiramo ćirilično i latinično O jednako.")
    rows = []
    all_files = [open(os.path.join(FOLDER, "literature-" + f + "-annotations.conllu"), "r", encoding="utf-8") for f in CONLLU_FILES]
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
        
        annotations = [c[10] if len(c) == 11 else "" for c in cols]
        if any(annotation  == "" for annotation in annotations):
            print(f"Greska u na liniji {line_number} - u jednom od fajlova nedostaje anotacija. Prostale anotacije su {" ".join(annotations)}.")
        
        # konverzija ćiriličnog O u  latinično
        annotations = [a if a != "О" else "O" for a in annotations]
        
        binary["milan-milica"].append( annotations[0] == annotations[1])    
        binary["milan-aleksa"].append( annotations[0] == annotations[2])   
        binary["milica-aleksa"].append( annotations[1] == annotations[2])   

        anotations_set = set(annotations)
        if len(anotations_set) != 1:
            decision = max(annotations, key=annotations.count)
            rows.append([line_number, *tokens, *annotations, decision])
            print(f"Greska u na liniji {line_number} - anotacije za token {tokens} se razlikuju: {annotations} - većinska odluka: {decision}")

    for f in all_files:
        f.close()
    
    df = pandas.DataFrame(rows, columns=["broj linije", "token", "Milan", "Milica", "Aleksa", "vecinska odluka"]) 
    df.to_excel(os.path.join(FOLDER, "calibration.xlsx"), header=True, index=False)
       
    
    print("\nbinarni stepeni saglasnosti")
    binary_precentages = []
    for key, val in binary.items():
        precentage = sum(val)/len(val)
        binary_precentages.append(precentage)
        print(f"{key}: {precentage:.5f}")
    print(f"prosek binarnih stepena saglasnosti {sum(binary_precentages)/len(binary_precentages):.5f}")


# to_connlu()
calibrate()