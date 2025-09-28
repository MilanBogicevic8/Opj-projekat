from pathlib import Path
from typing import Callable, Any
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
ACCURACY = "Accuracy"
PRECISION = "Precision"

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

def parse_token_tag_table(input: Path) -> pandas.DataFrame:
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
            return prefix+TAGS_MAPPING[tag[2:]]
        return "O"

    def get_tag(line: str) -> str|None:
        data = line.split("\t")
        if len(data) > 10:
            return data[10] or "O"
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

def match_tags(expect: Path, result: Path) -> tuple[pandas.DataFrame, pandas.DataFrame]:
    """
    Match expected NER annotation against result.
    Returns two tables.

    A table with stats:
    Tag | Expected count | Result count | Accuracy | Precision

    A table with differences in applied tags or parsed token:
    Expected token | Result token | Expected label | Result label

    If a token is not matched by either of the inputs,
    the corresponding table entries will be empty.
    """
    expect_table = parse_token_tag_table(expect)
    result_table = parse_token_tag_table(result)
    diff_indices = diff(expect_table[TOKEN].to_list(), result_table[TOKEN].to_list())
    diffs = pandas.DataFrame([(
        expect_table[TOKEN][i] if i else "",
        result_table[TOKEN][j] if j else "",
        expect_table[TAG][i] if i else "",
        result_table[TAG][j] if j else ""
    ) for i, j in diff_indices], columns=[EXPECTED_TOKEN, RESULT_TOKEN, EXPECTED_TAG, RESULT_TAG])

    
    tags = set(expect_table[TAG].unique()).union(result_table[TAG].unique())
    stats: list[tuple[str, int, int, float, float]] = []
    expected_total = expect_table.shape[0]
    result_total = result_table.shape[0]
    l=min(expected_total, result_total)
    matches = (expect_table[TAG][:l] == result_table[TAG][:l]).sum()
    accuracy = matches/result_table.shape[0]
    stats.append(("*", expected_total, result_total, accuracy, 0))
    for tag in sorted(tags):
        expected_count = (expect_table[TAG] == tag).sum()
        result_count = (result_table[TAG] == tag).sum()
        matches = ((expect_table[TAG][:l] == result_table[TAG][:l]) & (expect_table[TAG][:l] == tag)).sum()
        accuracy = matches / result_count if result_count else 1
        precision = matches / expected_count if expected_count else 1
        stats.append((tag, expected_count, result_count, accuracy, precision))

    stats_df = pandas.DataFrame(stats, columns=[TAG, EXPECTED_COUNT, RESULT_COUNT, ACCURACY, PRECISION])
    return stats_df, diffs

        
def export_stats(expect: Path, result: Path, output: Path):
    """
    Args:
        expect: The expected annotations as a conllu file.
        result: The output of the model to compare against, as a conllu file.
        output: The output path for the xlsx file.
    Returns: 
    """
    stats, diffs = match_tags(expect, result)

    diffs = diffs[(diffs[EXPECTED_TOKEN] != diffs[RESULT_TOKEN]) | (diffs[EXPECTED_TAG] != diffs[RESULT_TAG])]
    # Export both to the same Excel file
    with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
        stats.to_excel(writer, sheet_name='Stats', index=False)
        diffs.to_excel(writer, sheet_name='Diffs', index=False)

