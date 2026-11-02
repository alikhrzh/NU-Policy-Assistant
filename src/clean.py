import json
from pathlib import Path


def clean_text(text, page_number, cleaning_rule):
    clean_list = text.splitlines()
    for i in range(len(clean_list)):
        clean_list[i] = clean_list[i].strip()
    while (clean_list and clean_list[0] == ""):
        clean_list = clean_list[1:]
    match cleaning_rule["page_number_style"]:
        case "same_line":
            expected_header = f"{page_number} {' '.join(cleaning_rule['header'])}"
            if clean_list and " ".join(clean_list[0].split()) == expected_header:
                clean_list = clean_list[1:]
        case "separate_line":
            if clean_list and clean_list[0] == str(page_number):
                clean_list = clean_list[1:]
    while (clean_list and clean_list[0] == ""):
        clean_list = clean_list[1:]
    while(clean_list and clean_list[-1] == ""):
        clean_list.pop()
    if cleaning_rule["header"] and cleaning_rule["page_number_style"] == "separate_line":
        repeated_text = cleaning_rule["header"]
        length_repeated_text = len(repeated_text)
        if len(clean_list) >= length_repeated_text and clean_list[:length_repeated_text] == repeated_text:
            clean_list = clean_list[length_repeated_text:]
    if cleaning_rule["footer"]:
        repeated_text = cleaning_rule["footer"]
        length_repeated_text = len(repeated_text)
        if len(clean_list) >= length_repeated_text and clean_list[-length_repeated_text:] == repeated_text:
            clean_list = clean_list[:-length_repeated_text]
    for i in range(len(clean_list)):
        clean_list[i] = " ".join(clean_list[i].split())
    result = "\n".join(clean_list)
    return result.strip()


with open("data/cleaning_rules.json", "r", encoding="utf-8") as json_file:
    cleaning_rules = json.load(json_file)

rules_by_id = {
    rule["document_id"]: rule
    for rule in cleaning_rules
}
with open("data/sources.json", "r", encoding="utf-8") as json_file:
    documents = json.load(json_file)

for document in documents:
    path = Path("data/processed") / f"{document['document_id']}.json"
    with open(path, 'r', encoding="utf-8") as json_file:
        book = json.load(json_file)
    for page in book:
        result = clean_text(page["text"], page["page_number"], cleaning_rule = rules_by_id[document["document_id"]])
        page["clean_text"] = result

    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(book , json_file, ensure_ascii=False, indent=2)