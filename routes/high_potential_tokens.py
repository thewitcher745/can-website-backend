"""
This file contains the endpoints for the analysis section-related stuff.
"""

import yaml
from os import path, getcwd
import glob
from flask import abort, jsonify, request
from markdown import markdown

from app_prepare import app
from utils import get_slug

TOKENS_DIR = path.join(getcwd(), "static/high_potential_tokens")


@app.route("/api/high_potential_tokens", methods=["GET"])
@app.route("/api/high_potential_tokens/", methods=["GET"])
def list_high_potential_tokens():
    # List all high potential tokens, sorted by name
    n = request.args.get("n", default=0, type=int)
    tokens = []
    for filepath in glob.glob(path.join(TOKENS_DIR, "*.md")):
        meta, _ = parse_token_markdown_file(filepath)
        if not meta:
            continue
        slug = get_slug(filepath)
        token = {"slug": slug}
        token.update(meta)
        tokens.append(token)
    tokens.sort(key=lambda x: x.get("name", "").lower())
    if n == 0:
        return jsonify(tokens)
    return jsonify(tokens[:n])


def parse_token_markdown_file(filepath):
    """
    Parse a markdown file with a YAML frontmatter (---). Returns meta dict and markdown body.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1].strip())
            body = parts[2].strip()
            return meta, body
    return {}, content


@app.route("/api/high_potential_tokens/<slug>", methods=["GET"])
def get_high_potential_token(slug):
    # Get a specific high potential token (meta + HTML body)
    filepath = path.join(TOKENS_DIR, f"{slug}.md")
    if not path.isfile(filepath):
        abort(404)
    meta, md_content = parse_token_markdown_file(filepath)
    html_content = markdown(md_content)
    token = {"slug": slug}
    token.update(meta)
    token["content_html"] = html_content
    return jsonify(token)
