file_path = "../../data/literature/ana_karenjina.txt"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

tokens = text.replace("\n", " ").split(" ")

tokens = [t for t in tokens if t.strip() != ""]

print(f"Broj tokena u fajlu: {len(tokens)}")
