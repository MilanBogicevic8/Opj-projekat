import reldi_tokeniser
import os
import pandas as pd

path = os.path.join("data", "administrative_docments")
INPUT_FOLDER = os.path.join(path, "izvuceno_latinica")
OUTPUT_CONLLU = os.path.join(path, "administrative_texts.conllu")
OUTPUT_XLSX = os.path.join(path, "administrative_texts.xlsx")


def to_conllu():
    if os.path.exists(OUTPUT_CONLLU):
        os.remove(OUTPUT_CONLLU)
    with open(OUTPUT_CONLLU, "a", encoding="utf-8") as fout:
        for filename in os.listdir(INPUT_FOLDER):
            if filename.endswith(".txt"):
                input_path = os.path.join(INPUT_FOLDER, filename)
                
                with open(input_path, "r", encoding="utf-8") as fin:
                    text = fin.read()

                tokeni = reldi_tokeniser.run(text, 'sr', conllu=True, nonstandard=True, tag=True)
                fout.write(tokeni)
                
                print(f"Fajl: {filename}")

def to_excel():
    if os.path.exists(OUTPUT_XLSX):
        os.remove(OUTPUT_XLSX)

    rows = []
    with open(OUTPUT_CONLLU, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  
                rows.append([line])
                continue
            parts = line.split("\t")
            rows.append(parts)

    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_XLSX, header=False, index=False)

    print(f"Converted to exel")


to_conllu()
to_excel()