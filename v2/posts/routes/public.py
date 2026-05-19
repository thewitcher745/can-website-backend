from flask import Response

from app_prepare import app
from .base import BasePostsRouter
from ..models.base import PostType


class PublicPostsRouter(BasePostsRouter):
    """
    Wrapper class for endpoints on the public (non-admin) side.
    Omits "type" and "status" from responses.
    """

    @staticmethod
    def register_routes():
        """Registers the routes on the app."""
        app.add_url_rule(
            "/api/v2/<post_type>",
            view_func=PublicPostsRouter.get_public_posts,
            methods=["GET"],
        )
        app.add_url_rule(
            "/api/v2/<post_type>/<slug>",
            view_func=PublicPostsRouter.get_public_post,
            methods=["GET"],
        )

    @staticmethod
    def get_public_posts(post_type: PostType) -> tuple[Response, int]:
        """
        Get list of posts, public side.

        Query parameters:
            limit: Limit the number of posts shown, default None
            vip: If set, only show posts with is_vip of the same value

        Returns:
            JSON-ified post + status code
        """
        return BasePostsRouter.get_posts(post_type)

    @staticmethod
    def get_public_post(post_type: PostType, slug: str) -> tuple[Response, int]:
        """
        Get list of posts, public side.

        Returns:
            JSON-ified post
        """
        return BasePostsRouter.get_post(post_type, slug)
