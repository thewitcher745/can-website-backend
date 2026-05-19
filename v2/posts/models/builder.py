from typing import Any

from ..models.post import (
    AnalysisPost,
    ArticlePost,
    HighPotentialPost,
    ListedAnalysisPost,
    ListedArticlePost,
    ListedHighPotentialPost,
    PostType,
)


class PostBuilder:
    """Creates the correct type of post with the given data."""

    @staticmethod
    def build_post(
        post_type: PostType, data_dict: dict[str, Any]
    ) -> AnalysisPost | HighPotentialPost | ArticlePost:
        """Dispatch to appropriate post builder based on post type."""

        match post_type:
            case "analysis":
                return AnalysisPost.model_validate(data_dict)

            case "blog" | "news":
                return ArticlePost.model_validate(data_dict)

            case "high-potential":
                return HighPotentialPost.model_validate(data_dict)

    @staticmethod
    def build_post_from_row(
        row: dict[str, Any],
    ) -> ListedAnalysisPost | ListedArticlePost | ListedHighPotentialPost:
        """
        Builds the right type of post using the "flat" structure of an SQL row.
        """
        # The meta dict is a subset of the DB row
        meta_dict = row.copy()

        # Isolate the meta dict in a copy of the row
        del meta_dict["type"]
        del meta_dict["status"]
        del meta_dict["slug"]

        listed_post_data_dict = {
            "type": row["type"],
            "status": row["status"],
            "slug": row["slug"],
            "meta": meta_dict,
        }

        post_type: PostType = row["type"]

        match post_type:
            case "analysis":
                return ListedAnalysisPost.model_validate(listed_post_data_dict)

            case "blog" | "news":
                return ListedArticlePost.model_validate(listed_post_data_dict)

            case "high-potential":
                return ListedHighPotentialPost.model_validate(listed_post_data_dict)
