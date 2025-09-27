from datetime import datetime
from typing import TypedDict, Iterable
from pathlib import Path
import json

class ParsedTweet(TypedDict):
    timestamp: float
    content: str
    url: str
    id: str

RAW_DATA = Path(__file__)/"raw_data"
PARSED_DATA = Path(__file__)/"parsed_data"

def parse_entry(entry: dict) -> ParsedTweet:
    assert entry["content"]["itemContent"]["itemType"] == "TimelineTweet"
    content = entry["content"]["itemContent"]["tweet_results"]["result"]
    screen_name = content["core"]["screen_name"]
    created_at = content["legacy"]["created_at"]
    conversation_id_str = content["legacy"]["conversation_id_str"]
    return {
        "id": conversation_id_str,
        "timestamp": datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").timestamp(),
        "content": "",
        "url": f"https://x.com/{screen_name}/status/{conversation_id_str}"
    }

def parse_file(raw_file: Path) -> Iterable[ParsedTweet]:
    entries = json.loads(raw_file.read_text())["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]
    for entry in entries:
        try:
            yield parse_entry(entry)
        except Exception as e:
            print(f"Skipping an entry: {e}")


for raw_file in RAW_DATA.iterdir():
    parsed_file = PARSED_DATA/raw_file.name
    try:
        tweets = parse_file(raw_file)
        parsed_file.write_text(json.dumps(tweets, indent=3))
    except Exception as e:
        print(f"Skipping file {raw_file.name}: {e}")

