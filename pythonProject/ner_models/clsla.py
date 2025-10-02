import classla
from pathlib import Path
import sklearn.metrics
import re
import pandas

TAGS_MAPPING = {
    "DERIV-PER": "PER",
    "MISC": "O",
    "ADR": "LOC",
    "TOP": "LOC",
    "COURT": "ORG",
    "INST": "ORG",
    "COM": "ORG",
    "OTHORG": "ORG",
    "PERS": "PER",
    "PER": "PER",
    "LOC": "LOC",
    "ORG": "ORG"
}

# Column headers
TAG = "Tag"
EXPECTED_COUNT = "Expected count"
RESULT_COUNT = "Result count"
RECALL = "Recall"
PRECISION = "Precision"
F1_SCORE = "F1 score"

TOKEN = "Token"
EXPECTED_TOKEN = "Expected token"
RESULT_TOKEN = "Result token"
EXPECTED_TAG = "Expected tag"
RESULT_TAG = "Result tag"

def diff(left: list[str], right: list[str]) -> list[tuple[int|None,int|None]]:
    i, j = 0, 0
    ret: list[tuple[int|None, int|None]] = []
    while i < len(left) or j < len(right):
        x = 0
        found = False
        nexti = i
        nextj = j
        max_to_remove = len(left)-i-1 + len(right)-j-1
        for x in range(max_to_remove+1):
            for xi in range(max(0, x-(len(right)-j-1)),min(x+1,len(left)-i)):
                xj = x-xi
                nexti = i+xi
                nextj = j+xj
                if left[nexti] == right[nextj]:
                    found = True
                    break
            if found: break
        if not found:
            nexti = len(left)
            nextj = len(right)
        for i in range(i, nexti):
            ret.append((i, None))
        for j in range(j, nextj):
            ret.append((None, j))
        if found:
            ret.append((nexti, nextj))
        i = nexti+1
        j = nextj+1
    return ret

def parse_token_tag_table(input: Path, base: bool = False) -> pandas.DataFrame:
    """
    Extracts and parses the following table from a conllu file:
    Token | Tag
    """
    def get_token(line: str) -> str|None:
        if len(line) == 0 or line.startswith("#"):
            return None
        return line.split("\t")[1]
    
    def parse_tag(tag: str) -> str:
        if len(tag) < 2 or tag[1] != "-":
            return "O"
        prefix = tag[:2]
        if tag[2:] in TAGS_MAPPING:
            tag = TAGS_MAPPING[tag[2:]]
            return tag if base or tag == "O" else prefix+tag
        return "O"

    def get_tag(line: str) -> str|None:
        data = line.split("\t")
        if len(data) > 10:
            return parse_tag(data[10])
        if len(data) < 10:
            return None
        match = re.search(r"NER=([A-Z\-]+)", data[9])
        if match:
            return parse_tag(match.group(1))
        return "O"
    
    ret = []
    for line in input.read_text().split("\n"):
        token = get_token(line)
        tag = get_tag(line)
        if token and tag:
            ret.append((token, tag))
    return pandas.DataFrame(ret, columns=[TOKEN, TAG])

def match_tags(expect: Path, result: Path, base: bool=False) -> tuple[pandas.DataFrame, pandas.DataFrame, str]:
    """
    Match expected NER annotation against result.
    Returns two tables.

    A table with stats:
    Tag | Expected count | Result count | Precision | Recall | F1 Score

    A table with differences in applied tags or parsed tokens:
    Expected token | Result token | Expected label | Result label

    If a token is not matched by either of the inputs,
    the corresponding table entries will be empty.
    """
    expect_table = parse_token_tag_table(expect, base=base)
    result_table = parse_token_tag_table(result, base=base)
    diff_indices = diff(expect_table[TOKEN].to_list(), result_table[TOKEN].to_list())

    report = str(sklearn.metrics.classification_report(expect_table[TAG], result_table[TAG]))

    diffs = pandas.DataFrame([(
        expect_table[TOKEN][i] if i else "",
        result_table[TOKEN][j] if j else "",
        expect_table[TAG][i] if i else "",
        result_table[TAG][j] if j else ""
    ) for i, j in diff_indices], columns=[EXPECTED_TOKEN, RESULT_TOKEN, EXPECTED_TAG, RESULT_TAG])
    diffs = diffs[(diffs[EXPECTED_TOKEN] != diffs[RESULT_TOKEN]) | (diffs[EXPECTED_TAG] != diffs[RESULT_TAG])]
    
    tags = set(expect_table[TAG].unique()).union(result_table[TAG].unique()).difference({"O"})
    stats = []
    l=min(expect_table.shape[0], result_table.shape[0])

    for tag in sorted(tags):
        expected_count = (expect_table[TAG] == tag).sum()
        result_count = (result_table[TAG] == tag).sum()
        matches = ((expect_table[TAG][:l] == result_table[TAG][:l]) & (expect_table[TAG][:l] == tag)).sum()
        precision = matches / expected_count if expected_count else 1
        recall = matches / result_count if result_count else 1
        stats.append((tag, precision, recall, 2*precision*recall/(recall+precision) if matches else 0))

    #micro and macro avg
    def avg(table: list[list], col: int):
        if not table: return 0
        total = sum(it[col] for it in table)
        return total/len(table)
    stats.append(("macro avg", avg(stats, 1), avg(stats, 2), avg(stats, 3)))

    matches = ((expect_table[TAG][:l] == result_table[TAG][:l]) & (expect_table[TAG][:l] != "O")).sum()
    total_expect = (expect_table[TAG] != "O").sum()
    total_result = (result_table[TAG] != "O").sum()
    micro_precision = matches/total_result
    micro_recall = matches/total_expect
    stats.append(("micro avg", micro_precision, micro_recall, 2*micro_precision*micro_recall/(micro_recall+micro_precision) if matches else 0))
    stats_df = pandas.DataFrame(stats, columns=[TAG, PRECISION, RECALL, F1_SCORE])
    
    return stats_df, diffs, report
        
def export_stats(expect: Path, result: Path, output: Path, base: bool=False):
    """
    Args:
        expect: The expected annotations as a conllu file.
        result: The output of the model to compare against, as a conllu file.
        output: The output path for the xlsx file.
    Returns: 
    """
    stats, diffs, report = match_tags(expect, result, base=base)
    with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
        stats.to_excel(writer, sheet_name='Stats', index=False)
        diffs.to_excel(writer, sheet_name='Diffs', index=False)


classla.download('sr')
classla.download('sr', type="nonstandard")
standard = classla.Pipeline('sr', processors='tokenize,ner', tokenize_pretokenized=True)
nonstandard = classla.Pipeline('sr', processors='tokenize,ner', tokenize_pretokenized=True, type="nonstandard")
TEMP=Path("/tmp/classla")

def conllu_to_input(input: Path) -> str:
    lines = [it for it in input.read_text().split("\n") if len(it) > 0 and not it.startswith("#")]
    tokens = [it.split("\t")[1] for it in lines]
    return " ".join(tokens)

def evaluate(input: Path, output: Path, reports_output: Path):
    reports_output.mkdir(exist_ok=True)
    domain = output.name.split(".")[0]
    with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
        for type in ["standard", "nonstandard"]:
            for base in [False, True]:
                table_name = f"{type}_" + ("base" if base else "full")
                model = globals()[type]
                input_text = conllu_to_input(input)
                TEMP.write_text(model(input_text).to_conll())
                stats_table, diffs_table, report = match_tags(input, TEMP, base=base)
                stats_table = stats_table.round(2)
                stats_table.to_excel(writer, sheet_name=f"{table_name}-stats", index=False)
                diffs_table.to_excel(writer, sheet_name=f"{table_name}-diffs", index=False)
                (reports_output/f"{domain}_{table_name}").write_text(report)


input_dir = Path(__file__).parent.parent/"tokenized_files"
output_dir = Path(__file__).parent.parent/"evaluation"/"classla"
if __name__ == "__main__":
    for input in ["administrative_texts", "literature", "newspapers", "twitter", "combined"]:
        input_file = input_dir/f"{input}.conllu"
        output_file = output_dir/f"{input}.xlsx"
        reports_output = output_dir/"reports"
        print(f"Writing from {input_file} to {output_file}")
        evaluate(input_file, output_file, reports_output)