import pymupdf
import json

book = pymupdf.open("data/raw/sports-complex-rules.pdf")

pages = []
for page_number, page in enumerate(book, start=1):
    page_data = {}
    text_page = page.get_textpage_ocr(language="eng", dpi=300, full=True)
    text = page.get_text(textpage = text_page) or ""
    page_data["document_id"] = "sports-complex-rules"
    page_data["page_number"] = page_number
    page_data['text'] = text
    pages.append(page_data)
with open("data/processed/sports-complex-rules.json", "w", encoding="utf-8") as json_file:
    json.dump(pages, json_file, ensure_ascii=False, indent=2)
