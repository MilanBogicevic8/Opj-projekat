

from models import clsla, stats
from pathlib import Path

input_dir = Path(__file__).parent.parent/"tokenized_files"
output_dir = Path(__file__).parent.parent/"evaluation"/"classla"
for input in ["administrative_texts", "literature", "newspapers", "twitter", "combined"]:
    input_file = input_dir/f"{input}.conllu"
    output_file = output_dir/f"{input}.xlsx"
    print(f"Writing from {input_file} to {output_file}")
    clsla.evaluate(input_file, output_file)


