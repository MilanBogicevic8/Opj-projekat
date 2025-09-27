from datetime import datetime
from typing import TypedDict
from pathlib import Path
import json
from transliterate import translit
import reldi_tokeniser
import re
import pandas
from scraping.twitter.const import *

class ParsedTweet(TypedDict):
    timestamp: float
    content: str
    url: str
    id: str

RAW_DATA = Path(__file__).parent/"raw_data"
EMOJI_PATTERN = re.compile(
    "["
    "\U00010000-\U0010FFFF"
    "]+",
    flags=re.UNICODE
)

def parse_entry(entry: dict) -> ParsedTweet:
    assert entry["content"]["itemContent"]["itemType"] == "TimelineTweet"
    content = entry["content"]["itemContent"]["tweet_results"]["result"]
    screen_name = content["core"]["user_results"]["result"]["core"]["screen_name"]
    created_at = content["legacy"]["created_at"]
    conversation_id_str = content["legacy"]["conversation_id_str"]
    content = content["legacy"]["full_text"]
    content = translit(content, "sr", reversed=True)
    content = re.sub(r"https://\S+", "", content)
    content = EMOJI_PATTERN.sub("", content)

    if len(content.split(" ")) < 14:
        raise Exception(f"Tweet {content} is shorter than 14 words.")

    return {
        "id": conversation_id_str,
        "timestamp": datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").timestamp(),
        "content": re.sub(r"https://\S+", "", translit(content, "sr", reversed=True)),
        "url": f"https://x.com/{screen_name}/status/{conversation_id_str}"
    }

def parse_file(raw_file: Path) -> list[ParsedTweet]:
    entries = json.loads(raw_file.read_text())["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]
    ret: list[ParsedTweet] = []
    for entry in entries:
        try:
            ret.append(parse_entry(entry))
        except Exception as e:
            pass#print(f"Skipping an entry: {type(e)} {e}")
    return ret

all_tweets: list[ParsedTweet] = []
for raw_file in RAW_DATA.iterdir():
    try:
        tweets = parse_file(raw_file)
        all_tweets.extend(tweets)
        tokens = sum(len(it["content"].split(" ")) for it in tweets)
        print(f"Parsed {len(tweets)} tweets with {tokens} tokens from {raw_file.name}")
    except Exception as e:
        print(f"Skipping file {raw_file.name}: {e}")



DATA.mkdir(parents=True, exist_ok=True)
METADATA.write_text(json.dumps(all_tweets, indent=3, ensure_ascii=False))
INPUT.write_text("\n".join(it["content"] for it in all_tweets))
TOKENS_CONLLU.write_text(reldi_tokeniser.run(INPUT.read_text(), 'sr', conllu=True, nonstandard=True, tag=True))

table = [it.split("\t") if not it.startswith("#") and not len(it) == 0 else [it] for it in TOKENS_CONLLU.read_text().split("\n")]
for it in table:
    if len(it) != 10 and len(it) != 1:
        print(f"Faulty line {it}")
df = pandas.DataFrame(table)
df.to_excel(TOKENS_EXCEL)

total_tokens = len([it for it in TOKENS_CONLLU.read_text().split("\n") if not it.startswith("#") and not len(it) == 0])
print(f"TOTAL TOKENS: {total_tokens}")