from typing import Any

from ..models.post import PostStatus, PostType
from ..repos import PostRepo
from ..utils.exceptions import PublishedAtError, SlugConflictError, SlugImmutableError


class ServiceValidator:
    @staticmethod
    def ensure_unique_slug(post_type: PostType, slug: str) -> None:
        """
        Ensures the slug is unique within the given post type.

        Raises:
            SlugConflictError: If slug is not unique.
        """
        if PostRepo.slug_exists(post_type, slug):
            raise SlugConflictError(f"Slug {slug} already exists for type {post_type}")

    @staticmethod
    def enforce_publish_rules(status: PostStatus, meta_dict: dict[str, Any]) -> None:
        """
        Enforce publish date rules and mutate meta_dict if needed.

        Rules:
        - Draft posts: published_at must be None (force it)
        - Non-draft posts: published_at must be set (raise if missing)
        """
        if status == "draft":
            meta_dict["publishedAt"] = None  # Force None for drafts
        else:
            if meta_dict.get("publishedAt") is None:
                raise PublishedAtError("Non-draft posts must have publishedAt set")

    @staticmethod
    def ensure_same_slug(existing: str, new: str):
        """
        Ensures the new slug is the same as existing

        Raises:
            SlugImmutableError: If slug has changed from existing to new
        """

        if existing != new:
            raise SlugImmutableError("New post slug doesn't match existing.")
