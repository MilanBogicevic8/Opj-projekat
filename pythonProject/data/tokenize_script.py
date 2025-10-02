import reldi_tokeniser
import os
import pandas as pd

# domain name -> output file
DOMAINS = {
    "administrative_texts" : {
        "folder" :  os.path.join("data", "administrative_documents"),
        "input_folder" : "izvuceno_latinica",
    },
    "newspapers" : {
        "folder" : os.path.join("data",  "newspapers"),
        "input_folder" : "izvuceno",
    },
    "literature" : {
        "folder" : os.path.join("data",  "literature"),
        "input_folder" : ".",
    },
    "twitter" : {
        "folder" : os.path.join("data",  "twitter"),
        "input_folder" : ".",
    }
}


def to_conllu():
    for domain, folders in DOMAINS.items():
        print(domain)
        input_folder = os.path.join(folders["folder"], folders["input_folder"])
        output_file = os.path.join(folders["folder"],  domain + ".conllu")

        if os.path.exists(output_file):
            os.remove(output_file)

        with open(output_file, "a", encoding="utf-8") as fout:
            for filename in sorted(os.listdir(input_folder)):
                if filename.endswith(".txt"):
                    input_path = os.path.join(input_folder, filename)
                    
                    with open(input_path, "r", encoding="utf-8") as fin:
                        text = fin.read()

                    tokeni = reldi_tokeniser.run(text, 'sr', conllu=True, nonstandard=True, tag=True)
                    fout.write(tokeni)
                    
                    print(f"Fajl: {filename}")


def to_excel():
    for domain, folders in DOMAINS.items():
        input_file = os.path.join(folders["folder"],  domain + ".conllu")
        output_file = os.path.join(folders["folder"],  domain + ".xlsx")

        if os.path.exists(output_file):
            os.remove(output_file)

        rows = []
        with open(input_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):  
                    rows.append([line])
                    continue
                parts = line.split("\t")
                rows.append(parts)

        df = pd.DataFrame(rows)
        df.to_excel(output_file, index=False)

        print(f"Konvertovan {domain} u Excel")


to_conllu()
# to_excel()