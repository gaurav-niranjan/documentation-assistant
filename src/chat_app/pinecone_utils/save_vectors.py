import os
from dotenv import load_dotenv
from pinecone import Pinecone
import re

load_dotenv()

def split_markdown_by_h1(md_text):
    '''Converts Markdown file into  a list of text chunks
    Each chunk spans one section of the text, defined by the H1s (headings in markdown syntax)'''

    pattern = r"(?m)^# .+?(?=^# |\Z)"
    chunks = re.findall(pattern, md_text, re.DOTALL)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

#Convert the manual into a list of chunks:
with open("data_sources/lavafox.md", "r", encoding="utf-8") as f:
    md_content = f.read()

chunks = split_markdown_by_h1(md_content)

#Wrapping each chunk in the record format that pinecone wants:
records = []
for i, chunk in enumerate(chunks):
    records.append({
        "id": f"chunk-{i}",
        "chunk_text": chunk,
        "manual": "lavafox",
    })

#Insert records in Pinecone (it will create the chunks and embeddings automatically):
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

dense_index.upsert_records(
    namespace="lavafox",
    records=records,
)
