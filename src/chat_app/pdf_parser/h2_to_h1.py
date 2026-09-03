import re
from pathlib import Path


def promote_numbered_h2_to_h1(md_text):
    # Regex pattern to match "## <number>. <text>" at the beginning of a line
    pattern = r'(?m)^##\s+(\d+\.\s.+)'
    # Replace with "# <number>. <text>"
    return re.sub(pattern, r'# \1', md_text)

sources_dir = Path("data_sources")

input_path = sources_dir / "old_lavafox.md"
output_path = sources_dir / "lavafox.md"

with open(input_path, "r", encoding="utf-8") as f:
    md_content = f.read()

modified_content = promote_numbered_h2_to_h1(md_content)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(modified_content)

print("Markdown file updated successfully.")