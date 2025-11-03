"""
This file contains the endpoints for the analysis section-related stuff.
"""

from datetime import datetime
import yaml
from os import path, getcwd
import glob
from flask import abort, jsonify
from markdown import markdown

from app_prepare import app
from utils import get_slug
from routes.logos.get_logo_link import get_logo_link_from_symbol

ANALYSIS_DIR = path.join(getcwd(), "static/technical_analysis")
VIP_ANALYSIS_DIR = path.join(getcwd(), "static/technical_analysis/vip")


@app.route("/api/analysis", methods=["GET"])
@app.route("/api/analysis/", methods=["GET"])
def list_analysis_posts(n: int = 0):
    # List all analysis posts, sorted by latest update time
    posts = []
    for filepath in glob.glob(path.join(ANALYSIS_DIR, "*.md")):
        try:
            sections = parse_multi_markdown_file(filepath)

            if not sections:
                continue

            # Use the last metadata section for the latest update
            latest_meta = sections[-1]["meta"] if "meta" in sections[-1] else {}
            first_meta = sections[0]["meta"] if "meta" in sections[0] else {}
            time = latest_meta.get("time", "")

            # If the time field is mistyped, skip this post.
            if type(time) is not datetime or time.tzinfo is None:
                print(f"Invalid time format in {filepath}: {time}")
                continue

            slug = get_slug(filepath)
            post = {
                "slug": slug,
                "title": first_meta.get("title", slug),
                "time": time,  # Use latest update time
                "thumbnail": first_meta.get(
                    "thumbnail",
                    get_logo_link_from_symbol(first_meta.get("coins", [])[0]),
                ),
                "image": first_meta.get("image", ""),
                "author": first_meta.get("author", ""),
                "tags": first_meta.get("tags", []),
                "coins": first_meta.get("coins", []),
                "desc": first_meta.get("desc", ""),
            }

            posts.append(post)

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            continue

    posts.sort(key=lambda x: x["time"], reverse=True)

    if n == 0:
        return jsonify(posts)

    return jsonify(posts[:n])


@app.route("/api/vip_analysis", methods=["GET"])
@app.route("/api/vip_analysis/", methods=["GET"])
def list_vip_analysis_posts(n: int = 0):
    # List all analysis posts, sorted by latest update time
    posts = []
    for filepath in glob.glob(path.join(VIP_ANALYSIS_DIR, "*.md")):
        sections = parse_multi_markdown_file(filepath)
        if not sections:
            continue

        # Use the last metadata section for the latest update
        latest_meta = sections[-1]["meta"] if "meta" in sections[-1] else {}
        first_meta = sections[0]["meta"] if "meta" in sections[0] else {}
        time = latest_meta.get("time", "")

        # If the time field is mistyped, skip this post.
        if type(time) is str:
            continue

        slug = get_slug(filepath)
        post = {
            "slug": slug,
            "title": first_meta.get("title", slug),
            "time": time,  # Use latest update time
            "thumbnail": first_meta.get(
                "thumbnail", get_logo_link_from_symbol(first_meta.get("coins", [])[0])
            ),
            "image": first_meta.get("image", ""),
            "author": first_meta.get("author", ""),
            "tags": first_meta.get("tags", []),
            "coins": first_meta.get("coins", []),
            "desc": first_meta.get("desc", ""),
        }

        posts.append(post)

    posts.sort(key=lambda x: x["time"], reverse=True)

    if n == 0:
        return jsonify(posts)

    return jsonify(posts[:n])


def parse_multi_markdown_file(filepath):
    """
    Parse a markdown file with multiple YAML sections (---). Returns a list of dicts:
    [{meta: ..., body: ...}, ...]
    """

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("---")
    results = []

    idx = 1 if sections[0].strip() == "" else 0

    while idx < len(sections) - 1:
        meta = yaml.safe_load(sections[idx]) if sections[idx].strip() else {}
        body = sections[idx + 1].strip() if idx + 1 < len(sections) else ""
        results.append({"meta": meta, "body": body})
        idx += 2

    return results


@app.route("/api/analysis/<slug>", methods=["GET"])
def get_analysis_post(slug):
    # Get a specific analysis post (main + updates)

    filepath = path.join(ANALYSIS_DIR, f"{slug}.md")
    if not path.isfile(filepath):
        abort(404)

    sections = parse_multi_markdown_file(filepath)
    results = []

    for i, section in enumerate(sections):
        meta = section.get("meta", {})
        body = section.get("body", "")
        item = {"content_html": markdown(body)}

        if i == 0:
            item.update(
                {
                    "slug": slug,
                    "title": meta.get("title", slug),
                    "time": meta.get("time", ""),
                    "author": meta.get("author", ""),
                    "tags": meta.get("tags", []),
                    "desc": meta.get("desc", ""),
                    "thumbnail": meta.get("thumbnail", ""),
                }
            )

        else:
            item["time"] = meta.get("time", "")

        results.append(item)

    return jsonify(results)


@app.route("/api/vip_analysis/<slug>", methods=["GET"])
def get_vip_analysis_post(slug):
    # Get a specific analysis post (main + updates)

    filepath = path.join(VIP_ANALYSIS_DIR, f"{slug}.md")
    if not path.isfile(filepath):
        abort(404)

    sections = parse_multi_markdown_file(filepath)
    results = []

    for i, section in enumerate(sections):
        meta = section.get("meta", {})
        body = section.get("body", "")
        item = {"content_html": markdown(body)}

        if i == 0:
            item.update(
                {
                    "slug": slug,
                    "title": meta.get("title", slug),
                    "time": meta.get("time", ""),
                    "author": meta.get("author", ""),
                    "tags": meta.get("tags", []),
                    "desc": meta.get("desc", ""),
                    "thumbnail": meta.get("thumbnail", ""),
                }
            )

        else:
            item["time"] = meta.get("time", "")

        results.append(item)

    return jsonify(results)
