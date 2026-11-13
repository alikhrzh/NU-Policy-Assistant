import json
from pathlib import Path

for json_path in Path("data/processed").glob("*.json"):
    with open(json_path, "r", encoding="utf-8") as json_file:
        pages = json.load(json_file)

    empty_pages = []
    for page in pages:
        if not page["text"].strip():
            empty_pages.append(page["page_number"])

    print(f"{json_path.name} | страниц: {len(pages)} | пустые: {empty_pages}")