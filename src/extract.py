from pathlib import Path
from pypdf import PdfReader
import json

def extract_text_from_document(path_to_pdf, document_id, save_path):
    reader = PdfReader(path_to_pdf)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        page_data = {}
        text = page.extract_text() or ""
        page_data["document_id"] = document_id
        page_data["page_number"] = page_number
        page_data['text'] = text
        pages.append(page_data)
    with open(save_path, "w", encoding="utf-8") as json_file:
        json.dump(pages , json_file, ensure_ascii=False, indent=2)
    return pages

with open("data/sources.json", "r", encoding="utf-8") as json_file:
    documents = json.load(json_file)

Path("data/processed").mkdir(parents=True, exist_ok=True)
for document in documents:
    if document["text_status"] in ("ocr_required", "letter_spacing_issue"):
        print(f"Пропускаем: {document['filename']}")
        continue
    path_to_pdf = Path("data/raw") / document["filename"]
    save_path = Path("data/processed") / f"{document['document_id']}.json"
    pages = extract_text_from_document(
        path_to_pdf, document["document_id"], save_path
    )
    print(f"{document['document_id']}: сохранено {len(pages)} страниц")