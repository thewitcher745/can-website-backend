"""
This file contains the endpoints for the fundamental analysis section.
"""

import yaml
from os import path, getcwd
import glob
from flask import abort, jsonify
from markdown import markdown

from app_prepare import app
from utils import get_slug, get_random_thumbnail

FUNDAMENTAL_ANALYSIS_DIR = path.join(getcwd(), "static/fundamental_analysis")


def parse_fundamental_analysis_markdown_file(filepath):
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


@app.route("/api/fundamental", methods=["GET"])
@app.route("/api/fundamental/", methods=["GET"])
def list_fundamental_analysis_articles():
    # List all fundamental analysis articles
    articles = []

    for filepath in glob.glob(path.join(FUNDAMENTAL_ANALYSIS_DIR, "*.md")):
        meta, _ = parse_fundamental_analysis_markdown_file(filepath)
        slug = get_slug(filepath)
        article = {
            "slug": slug,
            "title": meta.get("title", slug),
            "time": meta.get("time", ""),
            "author": meta.get("author", ""),
            "tags": meta.get("tags", []),
            "desc": meta.get("desc", ""),
            "thumbnail": meta.get("thumbnail", get_random_thumbnail(seed=slug)),
        }
        articles.append(article)

    # Sort by time, newest first
    articles.sort(key=lambda x: x["time"], reverse=True)

    return jsonify(articles)


@app.route("/api/fundamental/<slug>", methods=["GET"])
def get_fundamental_analysis_article(slug):
    # Get a specific fundamental analysis article
    filepath = path.join(FUNDAMENTAL_ANALYSIS_DIR, f"{slug}.md")

    if not path.isfile(filepath):
        abort(404)

    meta, md_content = parse_fundamental_analysis_markdown_file(filepath)
    html_content = markdown(md_content)
    article = {
        "slug": slug,
        "title": meta.get("title", slug),
        "time": meta.get("time", ""),
        "author": meta.get("author", ""),
        "tags": meta.get("tags", []),
        "desc": meta.get("desc", ""),
        "content_html": html_content,
    }

    return jsonify(article)


@app.route("/api/recent_fundamental", methods=["GET"])
@app.route("/api/recent_fundamental/", methods=["GET"])
def get_top_fundamental():
    # Get the top 5 fundamental analysis articles
    articles = []

    for filepath in glob.glob(path.join(FUNDAMENTAL_ANALYSIS_DIR, "*.md")):
        meta, _ = parse_fundamental_analysis_markdown_file(filepath)
        slug = get_slug(filepath)
        article = {
            "slug": slug,
            "title": meta.get("title", slug),
            "time": meta.get("time", ""),
            "desc": meta.get("desc", ""),
            "thumbnail": meta.get("thumbnail", get_random_thumbnail(seed=slug)),
        }
        articles.append(article)

    # Sort by time, newest first
    articles.sort(key=lambda x: x["time"], reverse=True)

    articles = articles[:5]

    return jsonify(articles)
