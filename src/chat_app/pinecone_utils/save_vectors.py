import os
from dotenv import load_dotenv
from pinecone import Pinecone
import re
from pathlib import Path

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

files_to_embed = {
    "inkscape.pdf": "paintscape.md",
    "openmrs-guide.pdf": "openMRS.md",
    "thunderbird.pdf": "birdmail.md",
    "wordpress.pdf": "blogpress.md",
    "firefox.pdf": "lavafox.md"
}

source_dir = Path("data_sources")

def split_markdown_by_h1(md_text):
    '''Converts Markdown file into  a list of text chunks
    Each chunk spans one section of the text, defined by the H1s (headings in markdown syntax)'''

    pattern = r"(?m)^# .+?(?=^# |\Z)"
    chunks = re.findall(pattern, md_text, re.DOTALL)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

for pdf_name, md_name in files_to_embed.items():
    md_path = source_dir / md_name

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    chunks = split_markdown_by_h1(md_content)
    manual_name = md_path.stem

    records = []

    for i, chunk in enumerate(chunks):
        print(f"{manual_name}-chunk-{i}",)
        records.append({
            "id": f"{manual_name}-chunk-{i}",
            "chunk_text": chunk,
            "manual": manual_name
        })

    dense_index.upsert_records(namespace="all-gross", records=records)

print("Complete!")