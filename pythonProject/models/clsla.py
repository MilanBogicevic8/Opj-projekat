#type: ignore
import classla
from pathlib import Path
import pandas
from models import stats

classla.download('sr')
classla.download('sr', type="nonstandard")
standard = classla.Pipeline('sr', processors='tokenize,ner', tokenize_pretokenized=True)
nonstandard = classla.Pipeline('sr', processors='tokenize,ner', tokenize_pretokenized=True, type="nonstandard")
TEMP=Path("/tmp/classla")

def conllu_to_input(input: Path) -> str:
    lines = [it for it in input.read_text().split("\n") if len(it) > 0 and not it.startswith("#")]
    tokens = [it.split("\t")[1] for it in lines]
    return " ".join(tokens)

def evaluate(input: Path, output: Path):
    with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
        for type in ["standard", "nonstandard"]:
            for base in [False, True]:
                table_name = f"{type}-" + ("base" if base else "full")
                model = globals()[type]
                input_text = conllu_to_input(input)
                TEMP.write_text(model(input_text).to_conll())
                stats_table, diffs_table = stats.match_tags(input, TEMP, base=base)
                stats_table = stats_table.round(2)
                stats_table.to_excel(writer, sheet_name=f"{table_name}-stats", index=False)
                diffs_table.to_excel(writer, sheet_name=f"{table_name}-diffs", index=False)
