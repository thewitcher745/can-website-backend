import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

from supabase import Client, create_client


def validate_slug(value: Any) -> Tuple[bool, str]:
    if not isinstance(value, str) or not value.strip():
        return False, "Missing field: slug"
    slug = value.strip()
    # Keep slugs simple/safe for object storage paths
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}", slug):
        return False, "Invalid slug format"
    return True, ""


def validate_status(value: Any) -> Tuple[bool, str]:
    if not isinstance(value, str) or not value.strip():
        return False, "Missing field: status"
    status = value.strip().lower()
    if status not in {"published", "draft"}:
        return False, "Invalid status"
    return True, ""


def validate_editorjs_body(value: Any) -> Tuple[bool, str]:
    # Editor.js outputs an object like: { time, blocks: [...], version }
    if not isinstance(value, dict):
        return False, "Missing field: body"
    blocks = value.get("blocks")
    if not isinstance(blocks, list):
        return False, "Invalid body"
    return True, ""


def require_fields(data: Dict[str, Any], required: Iterable[str]) -> Tuple[bool, str]:
    for field in required:
        if field not in data:
            return False, f"Missing field: {field}"
        if data[field] is None:
            return False, f"Missing field: {field}"
        if isinstance(data[field], str) and data[field].strip() == "":
            return False, f"Missing field: {field}"
    return True, ""


def _get_supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("SUPABASE_API_URL")
    if not url:
        raise RuntimeError("SUPABASE_URL is not set")
    return url.rstrip("/")


def _get_supabase_key() -> str:
    # Prefer service role for server-side uploads.
    key = os.environ.get("SUPABASE_API_KEY")

    if not key:
        raise RuntimeError("SUPABASE_API_KEY is not set")
    return key


_supabase_client: Optional[Client] = None


def _get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(_get_supabase_url(), _get_supabase_key())
    return _supabase_client


def upload_json_to_supabase(
    bucket: str, object_path: str, payload: Dict[str, Any]
) -> str:
    """
    Uploads JSON to Supabase Storage and returns the public URL.

    Env vars required:
      - SUPABASE_URL (or SUPABASE_API_URL)
      - SUPABASE_API_KEY
    """

    object_path = object_path.lstrip("/")
    client = _get_supabase_client()
    storage = client.storage.from_(bucket)
    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        storage.upload(
            object_path,
            data_bytes,
            file_options={"content-type": "application/json", "upsert": "true"},
        )
    except Exception as e:
        raise RuntimeError(f"Supabase upload failed: {e}")

    try:
        public_url = storage.get_public_url(object_path)
        if isinstance(public_url, str) and public_url:
            return public_url
        if isinstance(public_url, dict):
            public_url_dict = cast(Dict[str, Any], public_url)
            for k in ("publicUrl", "publicURL", "url"):
                value = public_url_dict.get(k)
                if isinstance(value, str) and value:
                    return value
    except Exception:
        pass

    base_url = _get_supabase_url()
    return f"{base_url}/storage/v1/object/public/{bucket}/{object_path}"


def list_objects_in_supabase(bucket: str, prefix: str) -> List[Dict[str, Any]]:
    prefix = (prefix or "").strip().strip("/")
    client = _get_supabase_client()
    storage = client.storage.from_(bucket)

    try:
        items = storage.list(prefix)
    except TypeError:
        items = storage.list(path=prefix)

    if not isinstance(items, list):
        raise RuntimeError("Supabase list failed")

    results: List[Dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            results.append(item)
    return results


def download_json_from_supabase(bucket: str, object_path: str) -> Dict[str, Any]:
    object_path = object_path.lstrip("/")
    client = _get_supabase_client()
    storage = client.storage.from_(bucket)

    try:
        data = storage.download(object_path)
    except TypeError:
        data = storage.download(path=object_path)

    if isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    elif (
        isinstance(data, dict)
        and "data" in data
        and isinstance(data["data"], (bytes, bytearray))
    ):
        raw = bytes(data["data"])
    else:
        raw = cast(Any, data)

    try:
        decoded = (
            raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        )
        parsed = json.loads(decoded)
    except Exception as e:
        raise RuntimeError(f"Supabase download failed: invalid JSON ({e})")

    if not isinstance(parsed, dict):
        raise RuntimeError("Supabase download failed: JSON is not an object")
    return cast(Dict[str, Any], parsed)


def delete_object_from_supabase(bucket: str, object_path: str) -> None:
    object_path = object_path.lstrip("/")
    client = _get_supabase_client()
    storage = client.storage.from_(bucket)

    try:
        storage.remove([object_path])
    except TypeError:
        storage.remove(paths=[object_path])
