from pathlib import Path

DATA = Path(__file__).parent.parent.parent / "data" / "twitter"
METADATA = DATA/"metadata.json"
INPUT = DATA/"input.txt"
TOKENS_CONLLU = DATA/"tokenized.conllu"
TOKENS_EXCEL = DATA/"tokenized.xlsx"
ANNOTATIONS_EXCEL = DATA/"annotations.xlsx"
ANNOTATIONS_CONLLU = DATA/"annotations.conllu"