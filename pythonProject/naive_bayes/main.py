import os
import pandas as pd

import os
import pandas as pd

def conllu_to_xlsx(conllu_file_path):
    """
    Converts a CoNLL-U file to an XLSX file with the same name.
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

            # ✅ Normalizuj broj kolona na tačno 10
            if len(fields) > 10:
                fields = fields[:10]
            elif len(fields) < 10:
                fields += [""] * (10 - len(fields))

            sentence_data.append(fields)

        if sentence_data:
            data.extend(sentence_data)

    column_names = [
        'ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS',
        'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC'
    ]

    df = pd.DataFrame(data, columns=column_names)
    df.to_excel(xlsx_file_path, index=False)
    print(f"✔ '{conllu_file_path}' -> '{xlsx_file_path}'")


if __name__ == "__main__":
    file_names = [
        "../tokenized_files/literature.conllu",
        "../tokenized_files/administrative_texts.conllu",
        "../tokenized_files/newspapers.conllu",
        "../tokenized_files/twitter.conllu"
    ]

    for file in file_names:
        conllu_to_xlsx(file)
