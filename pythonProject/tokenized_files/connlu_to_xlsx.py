import os
import pandas as pd


def conllu_to_xlsx(conllu_file_path):
    """
    Converts a modified CoNLL-U file (with an extra annotation column) to an XLSX file.
    If the XLSX file exists, it will be overwritten.
    """
    xlsx_file_path = os.path.splitext(conllu_file_path)[0] + ".xlsx"

    if os.path.exists(xlsx_file_path):
        os.remove(xlsx_file_path)

    data = []
    with open(conllu_file_path, 'r', encoding='utf-8') as f:
        sentence_data = []
        for line in f:
            line = line.strip()
            if not line:
                if sentence_data:
                    data.extend(sentence_data)
                    sentence_data = []
                continue
            if line.startswith('#'):
                continue

            fields = line.split('\t')


            if len(fields) > 11:
                fields = fields[:11]
            elif len(fields) < 11:
                fields += [""] * (11 - len(fields))

            sentence_data.append(fields)

        if sentence_data:
            data.extend(sentence_data)

    column_names = [
        'ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS',
        'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC',
        'ANNOTATION'
    ]

    df = pd.DataFrame(data, columns=column_names)
    df.to_excel(xlsx_file_path, index=False)
    print(f"'{conllu_file_path}' -> '{xlsx_file_path}' (sa anotacijom)")


def xlsx_to_conllu(xlsx_file_path):
    """
    Converts an XLSX file (with annotation column) back to CoNLL-U format.
    """
    conllu_file_path = os.path.splitext(xlsx_file_path)[0] + ".conllu"

    if os.path.exists(conllu_file_path):
        os.remove(conllu_file_path)

    df = pd.read_excel(xlsx_file_path, dtype=str).fillna("_")

    with open(conllu_file_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # Rekonstruiši liniju sa 11 kolona
            fields = [
                row['ID'], row['FORM'], row['LEMMA'], row['UPOS'], row['XPOS'],
                row['FEATS'], row['HEAD'], row['DEPREL'], row['DEPS'], row['MISC'],
                row['ANNOTATION']
            ]
            f.write("\t".join(fields) + "\n")
        f.write("\n")  # kraj poslednje rečenice

    print(f"✔ '{xlsx_file_path}' -> '{conllu_file_path}'")


if __name__ == "__main__":
    file_names = [
        "../tokenized_files/literature.conllu",
        "../tokenized_files/administrative_texts.conllu",
        "../tokenized_files/newspapers.conllu",
        "../tokenized_files/twitter.conllu",
        "../tokenized_files/combined.conllu"
    ]

    # primer: CoNLL-U u XLSX
    for file in file_names:
        conllu_to_xlsx(file)

    # primer: nazad iz XLSX u CoNLL-U
    # for file in file_names:
    #     xlsx_file = os.path.splitext(file)[0] + ".xlsx"
    #     xlsx_to_conllu(xlsx_file)
