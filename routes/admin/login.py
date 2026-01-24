from datetime import datetime, timedelta, timezone
import os
from functools import wraps

from flask import jsonify, request, g
from werkzeug.security import check_password_hash
import jwt

from app_prepare import app


def _get_jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not set")
    return secret


def _issue_admin_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=2)).timestamp()),
        "type": "admin",
    }

    return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def token_required(fn):
    @wraps(fn)
    def _wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return jsonify({"error": "Missing token"}), 401

        try:
            payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        if payload.get("type") != "admin":
            return jsonify({"error": "Invalid token type"}), 401

        g.admin_username = payload.get("sub")
        return fn(*args, **kwargs)

    return _wrapper


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    print(request.data.decode("UTF-8"))
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    print(username, password)

    expected_username = os.environ.get("ADMIN_USERNAME")
    expected_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")

    print(expected_username, expected_password_hash)

    if not expected_username or not expected_password_hash:
        return jsonify({"error": "Admin credentials are not configured"}), 500

    if username != expected_username:
        print("wrong username")
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(expected_password_hash, password):
        print("wrong password")
        return jsonify({"error": "Invalid username or password"}), 401

    token = _issue_admin_token(username)
    return jsonify({"token": token, "token_type": "Bearer", "expires_in": 7200})


@app.route("/api/admin/me", methods=["GET"])
@token_required
def admin_me():
    return jsonify({"username": getattr(g, "admin_username", None)})
