import logging
from flask import Response, jsonify, request

from ..utils.exceptions import PostNotFoundError
from ..services import PostsService
from .utils import parse_bool
from ..models.base import PostType, ValidPostTypes

logger = logging.getLogger(__name__)


class BasePostsRouter:
    """Base class containing shared methods between Admin and PublicPostsRouter."""

    @staticmethod
    def _validate_post_type(post_type: str) -> tuple[Response, int] | None:
        """Validate the post type from the URL is valid."""
        if post_type not in ValidPostTypes:
            return jsonify(
                {
                    "error": "invalid_post_type",
                    "message": f"Invalid post type. Must be one of: {ValidPostTypes}",
                }
            ), 400

    @staticmethod
    def get_posts(post_type: PostType, admin: bool = False) -> tuple[Response, int]:
        """
        Get list of analysis posts.

        Args:
            admin: If True, keeps "type" and "status" fields, and allows unpublished
              results.

        Query parameters:
            limit: Limit the number of posts shown, default None
            vip: If set, only show posts with is_vip of the same value

        Returns:
            JSON-ified analysis post + status code
        """
        limit = request.args.get("limit", default=None, type=int)
        is_vip = request.args.get("vip", default=None, type=parse_bool)

        BasePostsRouter._validate_post_type(post_type)

        try:
            listed_posts = PostsService.list_posts_meta(
                post_type,
                allow_unpublished=True if admin else False,
                limit=limit,
                is_vip=is_vip,
            )

            # Serialize, jsonify and return published listed posts, omit type and status if
            # admin == True
            listed_post_json = [
                p.model_dump(
                    by_alias=True,
                    mode="json",
                    exclude=None if admin else {"type", "status"},
                )
                for p in listed_posts
            ]

            return jsonify({"data": listed_post_json}), 200

        except Exception as e:
            logger.error(
                f"Failed to list posts for type {post_type}: {e}", exc_info=True
            )
            return jsonify(
                {
                    "error": "internal_server_error",
                    "message": "Internal server error",
                }
            ), 500

    @staticmethod
    def get_post(
        post_type: PostType, slug: str, admin: bool = False
    ) -> tuple[Response, int]:
        """
        Get list of analysis posts.

        Args:
            admin: If True, keeps "type" and "status" fields, and allows unpublished
              results.

        Returns:
            JSON-ified analysis post
        """
        BasePostsRouter._validate_post_type(post_type)

        if not slug:
            return jsonify(
                {"error": "invalid_slug", "message": "Invalid post slug in URL"}
            ), 400

        try:
            post = PostsService.get_post(
                post_type, slug, allow_unpublished=True if admin else False
            )

            post_dict = post.model_dump(
                by_alias=True,
                mode="json",
                exclude=None if admin else {"type", "status"},
            )

            return jsonify({"data": post_dict}), 200

        except PostNotFoundError:
            return jsonify(
                {
                    "error": "post_not_found",
                    "message": f"Post {post_type}/{slug} not found",
                }
            ), 404

        except Exception as e:
            logger.error(
                f"Error when getting post {post_type}/{slug}: {e}", exc_info=True
            )

            return jsonify(
                {
                    "error": "internal_server_error",
                    "message": "Internal server error",
                }
            ), 500
