from datetime import datetime
from typing import TypedDict
from pathlib import Path
import json
from transliterate import translit
import reldi_tokeniser
import re

class ParsedTweet(TypedDict):
    timestamp: float
    content: str
    url: str
    id: str

RAW_DATA = Path(__file__).parent/"raw_data"
DATA = Path(__file__).parent.parent.parent / "data" / "twitter"

def parse_entry(entry: dict) -> ParsedTweet:
    assert entry["content"]["itemContent"]["itemType"] == "TimelineTweet"
    content = entry["content"]["itemContent"]["tweet_results"]["result"]
    screen_name = content["core"]["user_results"]["result"]["core"]["screen_name"]
    created_at = content["legacy"]["created_at"]
    conversation_id_str = content["legacy"]["conversation_id_str"]
    content = content["legacy"]["full_text"]
    content = translit(content, "sr", reversed=True)
    
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

total_tokens = 0
all_tweets: list[ParsedTweet] = []
for raw_file in RAW_DATA.iterdir():
    try:
        tweets = parse_file(raw_file)
        all_tweets.extend(tweets)
        tokens = sum(len(it["content"].split(" ")) for it in tweets)
        total_tokens += tokens
        print(f"Parsed {len(tweets)} tweets with {tokens} tokens from {raw_file.name}")
    except Exception as e:
        print(f"Skipping file {raw_file.name}: {e}")
print(f"TOTAL TOKENS: {total_tokens}")


DATA.mkdir(parents=True, exist_ok=True)
metadata = DATA/"metadata.json"
input = DATA/"input.txt"
tokenized = DATA/"tokenized.conllu"
temp = DATA/"temp.tsv"
metadata.write_text(json.dumps(all_tweets, indent=3, ensure_ascii=False))
input.write_text("\n".join(it["content"] for it in all_tweets))
tokenized.write_text(reldi_tokeniser.run(input.read_text(), 'sr', conllu=True, nonstandard=True, tag=True))