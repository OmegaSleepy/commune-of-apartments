import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

CONTENT_DIR = "content"
OUTPUT_DIR = "site"
TEMPLATES_DIR = "templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
template = env.get_template("listing.html")
index_template = env.get_template("index.html")

listings = []

def parse_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if text.startswith("---"):
        _, frontmatter, content = text.split("---", 2)
        meta = yaml.safe_load(frontmatter)
    else:
        meta = {}
        content = text

    html = markdown.markdown(content, extensions=["extra"])

    return meta, html

def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(CONTENT_DIR):
        if not file.endswith(".md"):
            continue

        path = os.path.join(CONTENT_DIR, file)
        meta, html = parse_markdown(path)

        slug = file.replace(".md", "")
        output_path = os.path.join(OUTPUT_DIR, f"{slug}.html")

        page = template.render(meta=meta, content=html)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(page)

        meta["slug"] = slug
        listings.append(meta)

    # Build index
    index_html = index_template.render(listings=listings)

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(index_html)

    explore_template = env.get_template("explore.html")

    explore_html = explore_template.render(listings=listings)

    with open(os.path.join(OUTPUT_DIR, "explore.html"), "w") as f:
        f.write(explore_html)

if __name__ == "__main__":
    build()