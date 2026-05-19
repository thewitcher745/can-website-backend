from datetime import datetime
from typing import Any

from ..models.builder import PostBuilder
from ..services.service_validation import ServiceValidator
from ..utils.exceptions import PostNotFoundError
from ..repos import PostRepo
from ..models.post import (
    AnalysisPost,
    ArticlePost,
    HighPotentialPost,
    ListedAnalysisPost,
    ListedArticlePost,
    ListedHighPotentialPost,
    PostType,
)


class PostsService:
    @staticmethod
    def create_post(post_type: PostType, raw_data: dict[str, Any]) -> str:
        """
        Creates a post of given type after validation and sanitization of the
        input data.

        Args:
            post_type: The type of post to be made.
            raw_data: dict-type data structure for the post being created.

        Returns:
            The final slug of the post made.
        """
        now = datetime.now()
        raw_data["meta"]["lastModifiedAt"] = now
        raw_data["meta"]["createdAt"] = now
        raw_data["type"] = post_type

        # Enforce the status/publish time relationship
        ServiceValidator.enforce_publish_rules(raw_data["status"], raw_data["meta"])

        # Create domain model
        post = PostBuilder.build_post(post_type, raw_data)

        # Ensure the sanitized slug from domain model is unique.
        ServiceValidator.ensure_unique_slug(post_type, post.slug)

        PostRepo.save_post(post)

        return post.slug

    @staticmethod
    def get_post(
        post_type: PostType, slug: str, allow_unpublished: bool = False
    ) -> AnalysisPost | ArticlePost | HighPotentialPost:
        """
        Gets a post with the given slug and type.

        Args:
            allow_unpublished: If False, raises PostNotFoundError if
              the post being fetched doesn't have status == "published"

        Returns:
            A domain model object of the appropriate type.
        """
        post = PostRepo.get_post(post_type, slug)

        if not allow_unpublished:
            if post.status != "published":
                raise PostNotFoundError(
                    "Public endpoint can't return unpublished posts."
                )

        return post

    @staticmethod
    def list_posts_meta(
        post_type: PostType,
        allow_unpublished: bool = False,
        limit: int | None = None,
        is_vip: bool | None = None,
    ) -> list[ListedAnalysisPost | ListedArticlePost | ListedHighPotentialPost]:
        """
        Returns a list of full listed posts of the given type. Limits to last $limit
        posts if limit is not None.

        Args:
            allow_unpublished: If False, only published posts will be returned.
            limit: Number of posts to return.
            is_vip: If set, only list posts that have the same is_vip field. Only applies
              to analysis posts.

        Returns:
            A list of posts without the content field.
        """
        filters: dict[str, Any] = {"type": post_type}

        if is_vip is not None:
            if post_type == "analysis":  # is_vip is only defined for analysis posts.
                filters["is_vip"] = is_vip

        if not allow_unpublished:
            filters["status"] = "published"

        posts = PostRepo.list_posts(filters=filters, limit=limit)

        return posts

    @staticmethod
    def update_post(post_type: PostType, slug: str, raw_data: dict[str, Any]) -> str:
        """
        Update a post of given type after validation and sanitization of the
        input data.

        Args:
            post_type: The type of post to update.
            slug: The slug of the post to update (This is the slug used not the one inside raw_data)
            raw_data: dict-type data structure for the post being updated.

        Returns:
            The final slug of the updated post.
        """
        raw_data["meta"]["lastModifiedAt"] = datetime.now()
        raw_data["type"] = post_type
        raw_data["slug"] = slug  # Force the raw_data dict to use the slug in the URL

        # Get existing post to check if slugs are the same
        existing = PostRepo.get_post(post_type, raw_data["slug"])

        # Enforce the status/publish time relationship
        ServiceValidator.enforce_publish_rules(raw_data["status"], raw_data["meta"])

        # Create domain model of the updated post
        post = PostBuilder.build_post(post_type, raw_data)

        # Ensure the sanitized slug from new domain model matches the old one.
        ServiceValidator.ensure_same_slug(existing=existing.slug, new=post.slug)

        PostRepo.save_post(post)

        return post.slug

    @staticmethod
    def delete_post(post_type: PostType, slug: str) -> None:
        """
        Deletes a post by type and slug.

        Raises:
            PostNotFoundError: If post doesn't exist
        """
        existing = PostRepo.get_post(post_type, slug)

        if not existing:
            raise PostNotFoundError(f"Post {post_type}/{slug} not found")

        PostRepo.delete_post(post_type, slug)
