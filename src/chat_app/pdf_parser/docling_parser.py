from docling.document_converter import DocumentConverter
from pathlib import Path

files_to_convert = {
    "inkscape.pdf": "paintscape.md",
    "openmrs-guide.pdf": "openMRS.md",
    "thunderbird.pdf": "birdmail.md",
    "wordpress.pdf": "blogpress.md"
}


source_dir = Path("data_sources")
converter = DocumentConverter()

for pdf_name, md_name in files_to_convert.items():
    pdf_path = source_dir / pdf_name
    md_path = source_dir / md_name

    doc = converter.convert(str(pdf_path)).document

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())

    print(f"Converted {pdf_name} to {md_name}")