"""
This file contains the endpoints for the blog section-related stuff.
"""

import yaml
from os import path, getcwd
import glob
from flask import abort, jsonify
from markdown import markdown

from app_prepare import app
from utils import get_slug

BLOG_DIR = path.join(getcwd(), "static/blog")


def parse_blog_markdown_file(filepath):
    # Read the file content and return the metadata and markdown content

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            md_content = parts[2].strip()

        else:
            meta = {}
            md_content = content

    else:
        meta = {}
        md_content = content

    return meta, md_content


@app.route("/api/blog", methods=["GET"])
def list_blog_posts():
    # List all blog posts
    posts = []

    for filepath in glob.glob(path.join(BLOG_DIR, "*.md")):
        meta, _ = parse_blog_markdown_file(filepath)
        slug = get_slug(filepath)
        post = {
            "slug": slug,
            "title": meta.get("title", slug),
            "time": meta.get("time", ""),
            "thumbnail_link": meta.get("thumbnail_link", ""),
            "author": meta.get("author", ""),
            "tags": meta.get("tags", []),
            "desc": meta.get("desc", ""),
        }

        posts.append(post)

    posts.sort(key=lambda x: x["time"], reverse=True)

    return jsonify(posts)


@app.route("/api/blog/<slug>", methods=["GET"])
def get_blog_post(slug):
    # Get a specific blog post

    filepath = path.join(BLOG_DIR, f"{slug}.md")

    if not path.isfile(filepath):
        abort(404)

    meta, md_content = parse_blog_markdown_file(filepath)
    html_content = markdown(md_content)
    post = {
        "slug": slug,
        "title": meta.get("title", slug),
        "time": meta.get("time", ""),
        "author": meta.get("author", ""),
        "tags": meta.get("tags", []),
        "desc": meta.get("desc", ""),
        "content_html": html_content,
    }

    return jsonify(post)
