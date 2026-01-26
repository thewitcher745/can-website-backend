from flask import jsonify, request

from app_prepare import app
from .helpers import (
    require_fields,
    upload_json_to_supabase,
)
from .login import token_required


def _normalize_str_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        return [part.strip() for part in s.split(",") if part.strip()]
    return [str(value).strip()] if str(value).strip() else []


@app.route("/api/admin/postNewArticle", methods=["POST"])
@token_required
def post_new_article():
    data = request.get_json(silent=True) or {}
    print(data)
    # ok, err = require_fields(data, ["type", "slug", "status", "published_at", "body"])
    # if not ok:
    #     return jsonify({"error": err}), 400

    type_ = str(data.get("type") or "").strip().lower()

    # ok, err = validate_slug(data.get("slug"))
    # if not ok:
    #     return jsonify({"error": err}), 400
    slug = data["slug"].strip()

    # ok, err = validate_status(data.get("status"))
    # if not ok:
    #     return jsonify({"error": err}), 400
    status = data["status"].strip().lower()

    # ok, err = validate_editorjs_body(data.get("body"))
    # if not ok:
    #     return jsonify({"error": err}), 400

    published_at = data.get("published_at")

    if type_ in {"blog", "news"}:
        ok, err = require_fields(
            data,
            ["title", "author"],
        )
        if not ok:
            return jsonify({"error": err}), 400

        payload = {
            "meta": {
                "type": type_,
                "slug": slug,
                "status": status,
                "published_at": published_at,
                "title": data.get("title"),
                "author": data.get("author"),
                "tags": _normalize_str_list(data.get("tags")),
            },
            "body": data.get("body"),
        }

        object_path = f"{type_}/{slug}.json"

    elif type_ == "analysis":
        ok, err = require_fields(data, ["title", "author", "isVip", "image"])
        if not ok:
            return jsonify({"error": err}), 400

        is_vip = bool(data.get("isVip"))
        payload = {
            "meta": {
                "type": type_,
                "slug": slug,
                "status": status,
                "published_at": published_at,
                "title": data.get("title"),
                "author": data.get("author"),
                "tags": _normalize_str_list(data.get("tags")),
                "vip": is_vip,
                "image": data.get("image"),
                "coins": _normalize_str_list(data.get("coins")),
            },
            "body": data.get("body"),
        }

        object_path = f"analysis/{'vip' if is_vip else 'public'}/{slug}.json"

    elif type_ == "high_potential":
        ok, err = require_fields(
            data,
            ["tokenName", "symbol", "category", "logo", "image"],
        )
        if not ok:
            return jsonify({"error": err}), 400

        payload = {
            "meta": {
                "type": type_,
                "slug": slug,
                "status": status,
                "published_at": published_at,
                "title": data.get("title"),
                "author": data.get("author"),
                "tags": _normalize_str_list(data.get("tags")),
                "tokenName": data.get("tokenName"),
                "symbol": data.get("symbol"),
                "category": data.get("category"),
                "logo": data.get("logo"),
                "image": data.get("image"),
            },
            "body": data.get("body"),
        }

        object_path = f"high_potential/{slug}.json"

    else:
        return jsonify({"error": "Invalid type"}), 400

    try:
        public_url = upload_json_to_supabase("articles", object_path, payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(
        {
            "ok": True,
            "type": type_,
            "slug": slug,
            "object_path": object_path,
            "public_url": public_url,
        }
    )
