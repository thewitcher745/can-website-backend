from typing import Any
from flask import Response, jsonify, request
import logging

from pydantic import ValidationError

from app_prepare import app
from v2.auth import AuthManager
from ..utils.exceptions import (
    PostNotFoundError,
    PublishedAtError,
    RepoError,
    SlugConflictError,
    SlugImmutableError,
)
from ..services import PostsService
from .base import BasePostsRouter
from ..models.base import PostType

logger = logging.getLogger(__name__)


class AdminPostsRouter(BasePostsRouter):
    """
    Wrapper class for endpoints on the public (non-admin) side.
    Omits "type" and "status" from responses.
    """

    @staticmethod
    def register_routes():
        """Registers the routes on the app."""
        app.add_url_rule(
            "/api/v2/admin/<post_type>",
            view_func=AdminPostsRouter.get_admin_posts,
            methods=["GET"],
        )
        app.add_url_rule(
            "/api/v2/admin/<post_type>/<slug>",
            view_func=AdminPostsRouter.get_admin_post,
            methods=["GET"],
        )
        app.add_url_rule(
            "/api/v2/admin/<post_type>/<slug>",
            view_func=AdminPostsRouter.delete_post,
            methods=["DELETE"],
        )
        app.add_url_rule(
            "/api/v2/admin/<post_type>",
            view_func=AdminPostsRouter.create_post,
            methods=["POST"],
        )
        app.add_url_rule(
            "/api/v2/admin/<post_type>/<slug>",
            view_func=AdminPostsRouter.update_post,
            methods=["PUT"],
        )

    @staticmethod
    @AuthManager.auth_required
    def get_admin_posts(post_type: PostType) -> tuple[Response, int]:
        """
        Get list of posts, admin side.

        Query parameters:
            limit: Limit the number of posts shown, default None
            vip: If set, only show posts with is_vip of the same value

        Returns:
            JSON-ified post + status code
        """
        return BasePostsRouter.get_posts(post_type, admin=True)

    @staticmethod
    @AuthManager.auth_required
    def get_admin_post(post_type: PostType, slug: str) -> tuple[Response, int]:
        """
        Get list of posts, admin side.

        Returns:
            JSON-ified post
        """
        return BasePostsRouter.get_post(post_type, slug, admin=True)

    @staticmethod
    @AuthManager.auth_required
    def create_post(post_type: PostType) -> tuple[Response, int]:
        """
        Creates a post of the given type, with the information in the request body.

        Returns:
            The slug of the created post
        """
        BasePostsRouter._validate_post_type(post_type)

        try:
            post_dict = request.get_json()
        except Exception:
            return jsonify(
                {"error": "invalid_request", "message": "Invalid request body"}
            ), 400

        try:
            slug = PostsService.create_post(post_type, post_dict)

            return jsonify({"data": {"slug": slug}}), 200

        except ValidationError as e:
            # Transform Pydantic errors into client-friendly format
            errors: list[dict[str, Any]] = []
            for err in e.errors():
                errors.append(
                    {
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                )

            return jsonify(
                {
                    "error": "validation_error",
                    "message": "Invalid data provided",
                    "details": errors,
                }
            ), 422

        except PublishedAtError:
            return jsonify(
                {
                    "error": "validation_error",
                    "message": "A post of the same type and slug already exists",
                    "details": {
                        "field": "publishedAt",
                        "message": "Publish time can't be empty.",
                        "type": "invalid_published_at",
                    },
                }
            ), 400

        except SlugConflictError:
            return jsonify(
                {
                    "error": "validation_error",
                    "message": "A post of the same type and slug already exists",
                    "details": {
                        "field": "slug",
                        "message": "Slug already exists",
                        "type": "slug_already_exists",
                    },
                }
            ), 409

        except RepoError as e:
            logger.error(f"Repository error during create_post: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500

        except Exception as e:
            logger.error(f"Unexpected error during create_post: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500

    @staticmethod
    @AuthManager.auth_required
    def update_post(post_type: PostType, slug: str) -> tuple[Response, int]:
        """
        Updates a post of the given type and slug.

        Returns:
            The slug of the updated post
        """
        BasePostsRouter._validate_post_type(post_type)

        try:
            post_dict = request.get_json()
        except Exception:
            return jsonify(
                {"error": "invalid_request", "message": "Invalid request body"}
            ), 400

        try:
            slug = PostsService.update_post(post_type, slug, post_dict)

            return jsonify({"data": {"slug": slug}}), 200

        except ValidationError as e:
            # Transform Pydantic errors into client-friendly format
            errors: list[dict[str, Any]] = []
            for err in e.errors():
                errors.append(
                    {
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                )

            return jsonify(
                {
                    "error": "validation_error",
                    "message": "Invalid data provided",
                    "details": errors,
                }
            ), 422

        except PublishedAtError:
            return jsonify(
                {
                    "error": "validation_error",
                    "message": "A post of the same type and slug already exists",
                    "details": {
                        "field": "publishedAt",
                        "message": "Publish time can't be empty.",
                        "type": "invalid_published_at",
                    },
                }
            ), 400

        except SlugImmutableError:
            return jsonify(
                {
                    "error": "validation_error",
                    "message": "New slug doesn't match existing post's slug.",
                    "details": {
                        "field": "slug",
                        "message": "Slug doesn't match.",
                        "type": "slug_immutable",
                    },
                }
            ), 409

        except PostNotFoundError:
            return jsonify(
                {
                    "error": "post_not_found",
                    "message": f"Post {post_type}/{slug} not found",
                }
            ), 404

        except RepoError as e:
            logger.error(f"Repository error during update_post: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500

        except Exception as e:
            logger.error(f"Unexpected error during update_post: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500

    @staticmethod
    @AuthManager.auth_required
    def delete_post(post_type: PostType, slug: str) -> tuple[Response, int]:
        """Deletes a post of the given type and slug."""
        BasePostsRouter._validate_post_type(post_type)

        try:
            PostsService.delete_post(post_type, slug)

            return jsonify({}), 200

        except PostNotFoundError:
            return jsonify(
                {
                    "error": "post_not_found",
                    "message": f"Post {post_type}/{slug} not found",
                }
            ), 404

        except RepoError as e:
            logger.error(f"Repository error during create_post: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify(
                {"error": "internal_server_error", "message": "Internal server error"}
            ), 500
