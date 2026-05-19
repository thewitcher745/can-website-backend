from flask import Response
from datetime import datetime, timezone, timedelta
from functools import wraps
import logging
import os
from typing import Any, Callable, ParamSpec, TypeVar, Union
from flask import g, jsonify, request
import jwt
from werkzeug.security import check_password_hash

from app_prepare import app

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class AuthManager:
    """
    Manager class for authentication utilities.

    Handles admin JWT token issuance, validation, and protected route decorators.
    """

    @staticmethod
    def register_routes():
        """Registers the auth endpoints."""
        app.add_url_rule(
            "/api/v2/auth/login",
            view_func=AuthManager.admin_login,
            methods=["POST"],
        )
        app.add_url_rule(
            "/api/v2/auth/me",
            view_func=AuthManager.admin_me,
            methods=["GET"],
        )

    @staticmethod
    def _get_jwt_secret() -> str:
        """
        Retrieves the JWT secret key from environment variables.

        Returns:
            The JWT secret key string.

        Raises:
            RuntimeError: If JWT_SECRET_KEY is not set in environment.
        """
        secret = os.environ.get("JWT_SECRET_KEY")
        if not secret:
            raise RuntimeError("JWT_SECRET_KEY is not set")
        return secret

    @staticmethod
    def _issue_admin_token(username: str) -> str:
        """
        Issues a new JWT token for an authenticated admin user.

        Args:
            username: The admin username to embed in the token.

        Returns:
            Encoded JWT token string with 2-hour expiration.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=2)).timestamp()),
            "type": "admin",
        }

        return jwt.encode(payload, AuthManager._get_jwt_secret(), algorithm="HS256")

    @staticmethod
    def auth_required(
        fn: Callable[P, T],
    ) -> Callable[P, Union[T, tuple[Response, int]]]:
        """
        Decorator that protects admin routes with JWT authentication.

        Expects a Bearer token in the Authorization header. Validates token
        signature, expiration, and admin type. On success, stores admin username
        in Flask's `g` object (`g.admin_username`).

        Returns:
            401 with error details if authentication fails.
            Otherwise, proceeds to the decorated function.
        """

        @wraps(fn)
        def _wrapper(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[T, tuple[Response, int]]:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify(
                    {"error": "invalid_header", "message": "Invalid or missing header"}
                ), 401

            token = auth_header.removeprefix("Bearer ").strip()
            if not token:
                return jsonify(
                    {"error": "invalid_token", "message": "Auth token missing"}
                ), 401

            try:
                payload = jwt.decode(
                    token, AuthManager._get_jwt_secret(), algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                return jsonify(
                    {"error": "token_expired", "message": "Auth token expired"}
                ), 401
            except jwt.InvalidTokenError:
                return jsonify(
                    {"error": "invalid_token", "message": "Invalid auth token"}
                ), 401

            if payload.get("type") != "admin":
                return jsonify(
                    {"error": "invalid_token", "message": "Invalid token type"}
                ), 401

            g.admin_username = payload.get("sub")
            return fn(*args, **kwargs)

        return _wrapper

    @staticmethod
    def admin_login():
        """
        Authenticates admin user and returns a JWT token.

        Expects JSON payload with 'username' and 'password' fields.
        Compares credentials against ADMIN_USERNAME and ADMIN_PASSWORD_HASH
        environment variables.

        Returns:
            On success: JSON with token, token_type, and expires_in (200)
            On failure: JSON error message with appropriate status code (401 or 500)
        """
        data: dict[str, Any] = request.get_json(silent=True) or {}

        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))

        expected_username = os.environ.get("ADMIN_USERNAME")
        expected_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")

        if not expected_username or not expected_password_hash:
            logger.error("Admin credentials not configured in environment")
            return jsonify(
                {
                    "error": "admin_credentials_missing",
                    "message": "Admin credentials missing",
                }
            ), 500

        if username != expected_username:
            logger.warning(f"Failed login attempt: invalid username '{username}'")
            return jsonify(
                {
                    "error": "invalid_username_password",
                    "message": "Invalid username or password",
                }
            ), 401

        if not check_password_hash(expected_password_hash, password):
            logger.warning(
                f"Failed login attempt: invalid password for username '{username}'"
            )
            return jsonify(
                {
                    "error": "invalid_username_password",
                    "message": "Invalid username or password",
                }
            ), 401

        token = AuthManager._issue_admin_token(username)

        return jsonify({"token": token, "token_type": "Bearer", "expires_in": 7200})

    @staticmethod
    @auth_required
    def admin_me() -> tuple[Response, int]:
        """
        Returns the currently authenticated admin username.

        Requires valid JWT token via @token_required decorator.

        Returns:
            JSON with username field (200)
        """
        username = g.admin_username
        return jsonify({"username": username}), 200
