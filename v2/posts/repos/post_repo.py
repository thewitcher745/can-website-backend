import json
from typing import Any, cast

from ..models.builder import PostBuilder
from ..models.post import (
    ListedAnalysisPost,
    ListedArticlePost,
    ListedHighPotentialPost,
)
from ..utils.exceptions import PostNotFoundError, RepoError
from .supabase_client import SupabaseClient
from ..models.post import ArticlePost, HighPotentialPost, AnalysisPost, PostType


PostModel = ArticlePost | AnalysisPost | HighPotentialPost
supabase_client = SupabaseClient()

BUCKET_NAME = "posts"
TABLE_NAME = "posts_meta"


class PostRepo:
    @staticmethod
    def _parse_bytes_to_json(data: bytes) -> dict[str, Any]:
        """
        Parses a bytes object to a dict-shaped JSON.
        Raises ValueError if the output shape is not a dict, or if
        decoding/parsing fails for whatever reason.
        """
        try:
            data_json = json.loads(data.decode("utf-8"))

            if not isinstance(data_json, dict):
                raise ValueError("Invalid JSON file contents.")

            data_json = cast(dict[str, Any], data_json)

            return data_json

        except Exception as e:
            raise ValueError(f"Error parsing JSON file: {e}")

    @staticmethod
    def slug_exists(post_type: PostType, slug: str) -> bool:
        """
        Returns True if slug of given type exists. False otherwise.
        """
        try:
            rows = supabase_client.db_select(
                TABLE_NAME, {"type": post_type, "slug": slug}
            )
            return len(rows) > 0
        except Exception as e:
            raise RepoError(f"Error while checking slug {slug} exists: {e}")

    @staticmethod
    def list_slugs(post_type: PostType) -> list[str]:
        """
        List all slugs from Supabase DB.

        Args:
            post_type: Type of posts to retrieve

        Returns:
            List of post slugs of given type
        """
        try:
            rows = supabase_client.db_select(TABLE_NAME, {"type": post_type})

            return [row["slug"] for row in rows]

        except Exception as e:
            raise RepoError(f"Failed to list slugs for type {post_type}: {e}")

    @staticmethod
    def list_posts(
        filters: dict[str, Any] = {}, limit: int | None = None
    ) -> list[ListedAnalysisPost | ListedArticlePost | ListedHighPotentialPost]:

        try:
            rows = supabase_client.db_select(TABLE_NAME, filters, limit)
        except Exception as e:
            raise RepoError(f"Failed to query posts_meta with filters {filters}: {e}")

        try:
            return [PostBuilder.build_post_from_row(row) for row in rows]

        except Exception as e:
            raise RepoError(
                f"Failed to deserialize posts_meta rows with filters {filters}: {e}"
            )

    @staticmethod
    def get_post(
        post_type: PostType, slug: str
    ) -> ArticlePost | AnalysisPost | HighPotentialPost:
        """
        Gets a single post with given type and slug.

        Args:
            post_type: Type of post to retrieve
            slug: The slug of the post to retrieve

        Returns:
            Post domain model
        """
        filename = f"{slug}.json"
        folder = post_type

        try:
            data = supabase_client.download_file(
                bucket_name=BUCKET_NAME, folder=folder, filename=filename
            )

            data_dict = PostRepo._parse_bytes_to_json(data)

        except FileNotFoundError:
            raise PostNotFoundError(
                f"Post of type '{post_type}' and slug '{slug}' not found."
            )

        except Exception as e:
            raise RepoError(f"Error while getting post: {e}")

        post = PostBuilder.build_post(post_type, data_dict)

        if post.type != post_type:
            raise RepoError(
                f"Type mismatch: file contains {post.type}, expected {post_type}"
            )

        return post

    @staticmethod
    def save_post(post: ArticlePost | AnalysisPost | HighPotentialPost):
        """
        Saves a post to the database (SQL + Storage).
        """
        # Prepare storage data (full post)
        data_dict = post.model_dump(by_alias=True, mode="json")
        json_bytes = json.dumps(data_dict, ensure_ascii=False, indent=2).encode("utf-8")

        filename = f"{post.slug}.json"
        folder = post.type

        # Prepare SQL data (no content, flat)
        # by_alias should be false since DB uses snake_case not camelCase
        row_dict = post.model_dump(exclude={"content"}, mode="json")
        # Flatten meta fields into root
        if "meta" in row_dict:
            meta_fields = row_dict.pop("meta")
            row_dict.update(meta_fields)

        try:
            # Upload to storage
            supabase_client.upload_file(
                bucket_name=BUCKET_NAME,
                folder=folder,
                filename=filename,
                data=json_bytes,
            )

            # Upsert to SQL
            supabase_client.db_upsert(TABLE_NAME, row_dict, conflict_column="type,slug")

        except Exception as e:
            # If DB update fails, remove the uploaded file.
            # If the file upload fails, delete_file is harmless.
            supabase_client.delete_file(BUCKET_NAME, folder, filename)

            raise RepoError(f"Error saving post '{post.slug}': {e}")

    @staticmethod
    def delete_post(post_type: PostType, slug: str):
        """
        Deletes a post with given type and slug from both SQL and storage.
        """
        filename = f"{slug}.json"
        folder = post_type

        try:
            # Delete from SQL first (No orphaned SQL rows)
            supabase_client.db_delete(TABLE_NAME, {"type": post_type, "slug": slug})

            # Then delete from storage
            supabase_client.delete_file(
                bucket_name=BUCKET_NAME, folder=folder, filename=filename
            )
        except Exception as e:
            raise RepoError(f"Error deleting post '{slug}': {e}")
