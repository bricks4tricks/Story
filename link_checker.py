import os
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DOMAIN = "logicandstories.com"
SKIP_DOMAINS = {
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.tailwindcss.com",
    "placehold.co",
}

CHECK_TAGS = [
    ("a", "href"),
    ("link", "href"),
    ("script", "src"),
    ("img", "src"),
    ("meta", "content"),
]

def categorize(tag_name, attrs):
    if tag_name == "link":
        return "css"
    if tag_name == "script":
        return "js"
    if tag_name == "img" or (tag_name == "meta" and attrs.get("property") == "og:image"):
        return "images"
    return "pages"

def html_files(root):
    templates_dir = os.path.join(root, "templates")
    for dirpath, _, filenames in os.walk(templates_dir):
        for name in filenames:
            if name.endswith((".html", ".h")):
                yield os.path.join(dirpath, name)

def resolve_local(path, current_file):
    # remove fragments and query strings
    path = path.split("#", 1)[0].split("?", 1)[0]
    if not path or path.startswith("javascript:") or path.startswith("mailto:"):
        return None
    if path.startswith("/api/"):
        return True  # assume dynamic API endpoint
    if path.startswith("//"):
        return None
    if path.startswith("/"):
        stripped = path.lstrip("/")
        candidates = [
            os.path.join(ROOT, stripped),
            os.path.join(ROOT, "templates", stripped),
            os.path.join(ROOT, "static", stripped),
        ]
    else:
        rel = os.path.normpath(os.path.join(os.path.dirname(current_file), path))
        candidates = [rel, os.path.join(ROOT, rel)]
    for cand in candidates:
        if os.path.exists(cand):
            return True
    return False

def check_url(url, tag_name, attrs, file_rel):
    parsed = urlparse(url)
    category = categorize(tag_name, attrs)
    if parsed.scheme in ("http", "https"):
        if parsed.netloc.endswith(BASE_DOMAIN) or parsed.netloc in SKIP_DOMAINS:
            return  # treat as internal/assumed valid or skipped
        try:
            resp = requests.head(url, allow_redirects=True, timeout=10)
            if resp.status_code >= 400:
                BROKEN[category].append((file_rel, url, str(resp.status_code)))
        except Exception as e:
            BROKEN[category].append((file_rel, url, str(e)))
    else:
        exists = resolve_local(url, os.path.join(ROOT, file_rel))
        if exists is False:
            BROKEN[category].append((file_rel, url, "missing file"))

BROKEN = {"css": [], "js": [], "images": [], "pages": []}

for file in html_files(ROOT):
    rel_file = os.path.relpath(file, ROOT)
    with open(file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    for tag_name, attr in CHECK_TAGS:
        if tag_name == "meta":
            tags = soup.find_all(tag_name, attrs={"property": "og:image"})
        else:
            tags = soup.find_all(tag_name)
        for tag in tags:
            url = tag.get(attr)
            if not url:
                continue
            check_url(url, tag_name, tag.attrs, rel_file)

if any(BROKEN.values()):
    for cat, items in BROKEN.items():
        if items:
            print(f"Broken {cat}:")
            for file_rel, url, reason in items:
                print(f"  {url} (referenced in {file_rel}) -> {reason}")
    sys.exit(1)
else:
    print("No broken links found.")
