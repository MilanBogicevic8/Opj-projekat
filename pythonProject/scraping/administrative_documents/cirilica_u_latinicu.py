import os
from transliterate import translit

# folder gde se nalaze txt fajlovi
INPUT_FOLDER = os.path.join("data", "administrative_documents", "izvuceno")
OUTPUT_FOLDER = os.path.join("data", "administrative_documents", "izvuceno_latinica")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".txt"):
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        converted = translit(content, "sr", reversed=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(converted)

        print(f"{filename} konvertovan.")