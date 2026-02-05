"""
This file contains the endpoints for the blog section-related stuff.
"""

from flask import abort, jsonify

from app_prepare import app
from utils import get_slug

from routes.admin.helpers import download_json_from_supabase, list_objects_in_supabase


@app.route("/api/news", methods=["GET"])
@app.route("/api/news/", methods=["GET"])
def list_news_posts():
    # List all news posts
    posts = []

    objects = list_objects_in_supabase("articles", "news")
    for obj in objects:
        name = obj.get("name") if isinstance(obj, dict) else None
        if not isinstance(name, str) or not name.endswith(".json"):
            continue

        slug = get_slug(name)
        object_path = f"news/{name}"
        try:
            doc = download_json_from_supabase("articles", object_path)
        except Exception:
            continue

        meta = doc.get("meta") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        if str(meta.get("status") or "").strip().lower() != "published":
            continue

        post = {"slug": slug, "meta": meta}

        posts.append(post)

    def _sort_key(item):
        meta = item.get("meta") if isinstance(item, dict) else None
        if not isinstance(meta, dict):
            return ""
        return str(meta.get("lastModifiedTime") or "")

    posts.sort(key=_sort_key, reverse=True)

    return jsonify(posts)


@app.route("/api/news/<slug>", methods=["GET"])
def get_news_post(slug):
    # Get a specific news post

    object_path = f"news/{slug}.json"
    try:
        doc = download_json_from_supabase("articles", object_path)
    except Exception:
        abort(404)

    meta = doc.get("meta") if isinstance(doc, dict) else None
    body = doc.get("body") if isinstance(doc, dict) else None
    if not isinstance(meta, dict):
        meta = {}

    if str(meta.get("status") or "").strip().lower() != "published":
        abort(404)

    return jsonify({"slug": slug, "meta": meta, "body": body})
