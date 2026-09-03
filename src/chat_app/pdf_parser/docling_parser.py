from docling.document_converter import DocumentConverter

source = "data_sources/firefox.pdf"
converter = DocumentConverter()
doc = converter.convert(source).document

with open("data_sources/lavafox.md", "w", encoding="utf-8") as f:
    f.write(doc.export_to_markdown())