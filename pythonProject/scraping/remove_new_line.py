import os

FOLDERS = ["administrative_documents/izvuceno_latinica", "literature", "newspapers/izvuceno", "twitter"]
OUTPUT_FOLDER = "izbaceni_novi_red"


for folder in FOLDERS:
    input_folder = os.path.join("data", folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_folder = os.path.join(OUTPUT_FOLDER, folder.split("/")[0])
            output_path = os.path.join(output_folder, filename)
            
            os.makedirs(output_folder, exist_ok=True)

            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # zameni samo \n, ostavi \n\n
            content = content.replace("\n\n", "<NEWPARA>")
            content = content.replace("\n", " ")
            content = content.replace("<NEWPARA>", "\n\n")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"{filename} konvertovan.")

