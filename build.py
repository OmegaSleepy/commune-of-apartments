import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
import re


CONTENT_DIR = "content"
OUTPUT_DIR = "docs"
TEMPLATES_DIR = "templates"
BASE_URL = "/commune-of-apartments/"

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

    # Fix image paths
    if BASE_URL != "/":
        html = html.replace('src="static/', f'src="{BASE_URL}static/')

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

        page = template.render(meta=meta, content=html, base=BASE_URL)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(page)

        meta["slug"] = slug
        listings.append(meta)

    # Build index
    index_html = index_template.render(listings=listings, base=BASE_URL)

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(index_html)

    explore_template = env.get_template("explore.html")

    explore_html = explore_template.render(listings=listings, base=BASE_URL)

    with open(os.path.join(OUTPUT_DIR, "explore.html"), "w") as f:
        f.write(explore_html)




def parse_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if text.startswith("---"):
        _, frontmatter, content = text.split("---", 2)
        meta = yaml.safe_load(frontmatter)
    else:
        meta = {}
        content = text

    # 1. Extract all image URLs from the markdown content before converting to HTML
    # This looks for markdown syntax like ![alt](url)
    gallery_images = re.findall(r'!\[.*?\]\((.*?)\)', content)

    # 2. Remove those images from the content so they don't show up under "Description"
    content_cleaned = re.sub(r'!\[.*?\]\((.*?)\)', '', content)

    html = markdown.markdown(content_cleaned, extensions=["extra"])

    # Fix image paths for the gallery list
    if BASE_URL != "/":
        html = html.replace('src="static/', f'src="{BASE_URL}static/')
        gallery_images = [img.replace('static/', f'{BASE_URL}static/') for img in gallery_images]

    # Add the images to the meta dictionary so Jinja can see them
    meta['gallery'] = gallery_images

    return meta, html

if __name__ == "__main__":
    build()