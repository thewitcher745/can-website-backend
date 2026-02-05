from typing import Any, Dict, List, Optional, Tuple

from flask import jsonify, request

from app_prepare import app
from .helpers import (
    delete_object_from_supabase,
    download_json_from_supabase,
    list_objects_in_supabase,
    validate_slug,
)
from .login import token_required


def _extract_slug_from_name(name: str) -> str:
    if name.endswith(".json"):
        return name[: -len(".json")]
    return name


def _meta_title(meta: Dict[str, Any]) -> Any:
    if meta.get("title") is not None:
        return meta.get("title")
    if meta.get("name") is not None:
        return meta.get("name")
    return None


def _build_object_path(
    type_: str, slug: str, is_vip: Optional[bool]
) -> Tuple[bool, str, str]:
    if type_ in {"blog", "news", "high_potential"}:
        return True, "", f"{type_}/{slug}.json"

    if type_ == "analysis":
        if is_vip is None:
            return False, "Missing field: isVip", ""
        return True, "", f"analysis/{'vip' if is_vip else 'public'}/{slug}.json"

    return False, "Invalid type", ""


@app.route("/api/admin/articles", methods=["GET"])
@token_required
def list_articles():
    type_filter = request.args.get("type")
    type_filter = (
        type_filter.strip().lower()
        if isinstance(type_filter, str) and type_filter.strip()
        else None
    )

    results: List[Dict[str, Any]] = []

    prefixes: List[Tuple[str, Optional[bool], str]]
    if type_filter:
        if type_filter == "analysis":
            prefixes = [
                ("analysis", True, "analysis/vip"),
                ("analysis", False, "analysis/public"),
            ]
        else:
            prefixes = [(type_filter, None, type_filter)]
    else:
        prefixes = [
            ("blog", None, "blog"),
            ("news", None, "news"),
            ("high_potential", None, "high_potential"),
            ("analysis", True, "analysis/vip"),
            ("analysis", False, "analysis/public"),
        ]

    for type_, is_vip, prefix in prefixes:
        try:
            objects = list_objects_in_supabase("articles", prefix)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        for obj in objects:
            name = obj.get("name") if isinstance(obj, dict) else None
            if not isinstance(name, str) or not name.endswith(".json"):
                continue

            slug = _extract_slug_from_name(name)
            ok, err = validate_slug(slug)
            if not ok:
                continue

            object_path = f"{prefix}/{name}" if prefix else name
            try:
                doc = download_json_from_supabase("articles", object_path)
            except Exception:
                continue

            meta = doc.get("meta") if isinstance(doc, dict) else None
            if not isinstance(meta, dict):
                meta = {}

            results.append(
                {
                    "slug": slug,
                    "type": type_,
                    "status": meta.get("status"),
                    "time": meta.get("time"),
                    "lastModifiedTime": meta.get("lastModifiedTime"),
                    "title": _meta_title(meta),
                    "isVip": is_vip if type_ == "analysis" else None,
                }
            )

    def _sort_key(item: Dict[str, Any]):
        return str(item.get("lastModifiedTime") or item.get("time") or "")

    results.sort(key=_sort_key, reverse=True)
    return jsonify({"ok": True, "items": results})


@app.route("/api/admin/getArticle", methods=["GET"])
@token_required
def get_article():
    type_ = request.args.get("type")
    slug = request.args.get("slug")

    type_ = type_.strip().lower() if isinstance(type_, str) else ""
    slug = slug.strip() if isinstance(slug, str) else ""
    ok, err = validate_slug(slug)
    if not ok:
        return jsonify({"error": err}), 400

    if type_ == "analysis":
        vip_raw = request.args.get("isVip")
        if vip_raw is None:
            # Try VIP first, then public
            candidates = [
                (True, f"analysis/vip/{slug}.json"),
                (False, f"analysis/public/{slug}.json"),
            ]
        else:
            vip = str(vip_raw).strip().lower() in {"1", "true", "yes"}
            candidates = [(vip, f"analysis/{'vip' if vip else 'public'}/{slug}.json")]

        last_err: Optional[Exception] = None
        for vip, object_path in candidates:
            try:
                doc = download_json_from_supabase("articles", object_path)
                return jsonify(
                    {
                        "ok": True,
                        "type": "analysis",
                        "slug": slug,
                        "isVip": vip,
                        "data": doc,
                    }
                )
            except Exception as e:
                last_err = e

        return jsonify({"error": str(last_err) if last_err else "Not found"}), 404

    ok2, err2, object_path = _build_object_path(type_, slug, None)
    if not ok2:
        return jsonify({"error": err2}), 400

    try:
        doc = download_json_from_supabase("articles", object_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"ok": True, "type": type_, "slug": slug, "data": doc})


@app.route("/api/admin/deleteArticle", methods=["DELETE"])
@token_required
def delete_article():
    type_ = request.args.get("type")
    slug = request.args.get("slug")

    type_ = type_.strip().lower() if isinstance(type_, str) else ""
    slug = slug.strip() if isinstance(slug, str) else ""

    ok, err = validate_slug(slug)
    if not ok:
        return jsonify({"error": err}), 400

    if type_ == "analysis":
        vip_raw = request.args.get("isVip")
        if vip_raw is None:
            candidates = [
                (True, f"analysis/vip/{slug}.json"),
                (False, f"analysis/public/{slug}.json"),
            ]
        else:
            vip = str(vip_raw).strip().lower() in {"1", "true", "yes"}
            candidates = [(vip, f"analysis/{'vip' if vip else 'public'}/{slug}.json")]

        deleted: List[Dict[str, Any]] = []
        errors: List[str] = []
        for vip, object_path in candidates:
            try:
                delete_object_from_supabase("articles", object_path)
                deleted.append({"isVip": vip, "object_path": object_path})
            except Exception as e:
                errors.append(str(e))

        if deleted:
            return jsonify(
                {
                    "ok": True,
                    "type": "analysis",
                    "slug": slug,
                    "deleted": deleted,
                    "errors": errors,
                }
            )
        return jsonify({"error": errors[-1] if errors else "Delete failed"}), 404

    ok2, err2, object_path = _build_object_path(type_, slug, None)
    if not ok2:
        return jsonify({"error": err2}), 400

    try:
        delete_object_from_supabase("articles", object_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"ok": True, "type": type_, "slug": slug, "deleted": object_path})
