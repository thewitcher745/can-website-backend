"""
This file contains the endpoints for the analysis section-related stuff.
"""

from flask import abort, jsonify

from app_prepare import app
from utils import get_slug
from routes.admin.helpers import download_json_from_supabase, list_objects_in_supabase


@app.route("/api/analysis", methods=["GET"])
@app.route("/api/analysis/", methods=["GET"])
def list_analysis_posts(n: int = 0):
    # List all public analysis posts
    posts = []

    objects = list_objects_in_supabase("articles", "analysis")
    for obj in objects:
        name = obj.get("name") if isinstance(obj, dict) else None
        if not isinstance(name, str) or not name.endswith(".json"):
            continue

        slug = get_slug(name)
        object_path = f"analysis/{name}"
        try:
            doc = download_json_from_supabase("articles", object_path)
        except Exception:
            continue

        meta = doc.get("meta") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        if str(meta.get("status") or "").strip().lower() != "published":
            continue

        if meta.get("isVip"):
            continue

        post = {"slug": slug, "meta": meta}
        posts.append(post)

    def _sort_key(item):
        meta = item.get("meta") if isinstance(item, dict) else None
        if not isinstance(meta, dict):
            return ""
        return str(meta.get("lastModifiedTime") or "")

    posts.sort(key=_sort_key, reverse=True)

    if n == 0:
        return jsonify(posts)
    return jsonify(posts[:n])


@app.route("/api/analysis/coin/<symbol>", methods=["GET"])
def list_analysis_posts_by_coin(symbol: str):
    # List public analysis posts that reference a specific coin (case-insensitive match)
    if not symbol:
        abort(400, description="Coin name is required.")

    symbol_normalized = symbol.strip().lower()
    posts = []

    objects = list_objects_in_supabase("articles", "analysis")
    for obj in objects:
        name = obj.get("name") if isinstance(obj, dict) else None
        if not isinstance(name, str) or not name.endswith(".json"):
            continue

        slug = get_slug(name)
        object_path = f"analysis/{name}"
        try:
            doc = download_json_from_supabase("articles", object_path)
        except Exception:
            continue

        meta = doc.get("meta") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        if str(meta.get("status") or "").strip().lower() != "published":
            continue

        if meta.get("isVip"):
            continue

        coins = [c.lower() for c in meta.get("coins", [])]
        if symbol_normalized not in coins:
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


@app.route("/api/vip_analysis/coin/<symbol>", methods=["GET"])
def list_vip_analysis_posts_by_coin(symbol: str):
    # List VIP analysis posts that reference a specific coin (case-insensitive match)
    if not symbol:
        abort(400, description="Coin name is required.")

    symbol_normalized = symbol.strip().lower()
    posts = []

    objects = list_objects_in_supabase("articles", "analysis")
    for obj in objects:
        name = obj.get("name") if isinstance(obj, dict) else None
        if not isinstance(name, str) or not name.endswith(".json"):
            continue

        slug = get_slug(name)
        object_path = f"analysis/{name}"
        try:
            doc = download_json_from_supabase("articles", object_path)
        except Exception:
            continue

        meta = doc.get("meta") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        if str(meta.get("status") or "").strip().lower() != "published":
            continue

        if not meta.get("isVip"):
            continue

        coins = [c.lower() for c in meta.get("coins", [])]
        if symbol_normalized not in coins:
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


@app.route("/api/vip_analysis", methods=["GET"])
@app.route("/api/vip_analysis/", methods=["GET"])
def list_vip_analysis_posts(n: int = 0):
    # List all VIP analysis posts
    posts = []

    objects = list_objects_in_supabase("articles", "analysis")
    for obj in objects:
        name = obj.get("name") if isinstance(obj, dict) else None
        if not isinstance(name, str) or not name.endswith(".json"):
            continue

        slug = get_slug(name)
        object_path = f"analysis/{name}"
        try:
            doc = download_json_from_supabase("articles", object_path)
        except Exception:
            continue

        meta = doc.get("meta") if isinstance(doc, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        if str(meta.get("status") or "").strip().lower() != "published":
            continue

        if not meta.get("isVip"):
            continue

        post = {"slug": slug, "meta": meta}
        posts.append(post)

    def _sort_key(item):
        meta = item.get("meta") if isinstance(item, dict) else None
        if not isinstance(meta, dict):
            return ""
        return str(meta.get("lastModifiedTime") or "")

    posts.sort(key=_sort_key, reverse=True)

    if n == 0:
        return jsonify(posts)
    return jsonify(posts[:n])


@app.route("/api/analysis/<slug>", methods=["GET"])
def get_analysis_post(slug):
    # Get a specific public analysis post

    object_path = f"analysis/{slug}.json"
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

    if meta.get("isVip"):
        abort(404)

    return jsonify({"slug": slug, "meta": meta, "body": body})


@app.route("/api/vip_analysis/<slug>", methods=["GET"])
def get_vip_analysis_post(slug):
    # Get a specific VIP analysis post

    object_path = f"analysis/{slug}.json"
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

    if not meta.get("isVip"):
        abort(404)

    return jsonify({"slug": slug, "meta": meta, "body": body})
