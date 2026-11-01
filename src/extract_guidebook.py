import pymupdf
import json

guidebook = pymupdf.open("data/raw/academic-mobility-guidebook-2026.pdf")

pages = []
for page_number, page in enumerate(guidebook, start=1):
    page_data = {}
    text = page.get_text() or ""
    page_data["document_id"] = "academic-mobility-guidebook-2026"
    page_data["page_number"] = page_number
    page_data['text'] = text
    pages.append(page_data)
with open("data/processed/academic-mobility-guidebook-2026.json", "w", encoding="utf-8") as json_file:
    json.dump(pages, json_file, ensure_ascii=False, indent=2)
