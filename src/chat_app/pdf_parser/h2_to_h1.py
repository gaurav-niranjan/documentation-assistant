import re
from pathlib import Path


def promote_numbered_h2_to_h1(md_text):
    # Regex pattern to match "## <number>. <text>" at the beginning of a line
    pattern = r'(?m)^##\s+(\d+\.\s.+)'
    # Replace with "# <number>. <text>"
    return re.sub(pattern, r'# \1', md_text)

files_to_convert = {
    "inkscape.pdf": "paintscape.md",
    "openmrs-guide.pdf": "openMRS.md",
    "thunderbird.pdf": "birdmail.md",
    "wordpress.pdf": "blogpress.md"
}


sources_dir = Path("data_sources")

for pdf_name, md_name in files_to_convert.items():
    md_path = sources_dir / md_name

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    modified_content = promote_numbered_h2_to_h1(md_content)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    print(f"Converted {md_name} markdown headers")
