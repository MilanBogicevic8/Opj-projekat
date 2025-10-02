import os


FOLDERS = [os.path.join("administrative_documents", "izvuceno_latinica"), os.path.join("newspapers", "izvuceno"), "literature", "twitter"]


for folder in FOLDERS:
    input_folder = os.path.join("data", folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file = os.path.join(input_folder, filename)

            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # zameni samo \n, ostavi \n\n
            content = content.replace("\n\n", "<NEWPARA>")
            content = content.replace("\n", " ")
            content = content.replace("<NEWPARA>", "\n\n")

            with open(file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"{filename} konvertovan.")

