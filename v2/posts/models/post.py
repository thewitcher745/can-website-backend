from typing import Annotated, Generic
from pydantic import BaseModel, StringConstraints, field_validator

from .sanitizers import Sanitizers
from .base import PostStatus, PostType, TContent, TMeta
from .content import AnalysisContent, ArticleContent
from .meta import AnalysisMeta, ArticleMeta, HighPotentialMeta, WhitespaceStrippedString


class BasePost(BaseModel, Generic[TMeta, TContent]):
    type: PostType
    slug: Annotated[
        WhitespaceStrippedString, StringConstraints(min_length=5, max_length=80)
    ]
    meta: TMeta
    content: TContent
    status: PostStatus

    @field_validator("slug", mode="before")
    @classmethod
    def sanitize_slug(cls, raw_slug: str) -> str:
        return Sanitizers.slug(raw_slug)


class ArticlePost(BasePost[ArticleMeta, ArticleContent]):
    pass


class AnalysisPost(BasePost[AnalysisMeta, AnalysisContent]):
    pass


class HighPotentialPost(BasePost[HighPotentialMeta, ArticleContent]):
    pass


class BaseListedPost(BaseModel, Generic[TMeta]):
    slug: Annotated[
        WhitespaceStrippedString, StringConstraints(min_length=5, max_length=80)
    ]
    type: PostType
    status: PostStatus
    meta: TMeta

    @field_validator("slug", mode="before")
    @classmethod
    def sanitize_slug(cls, raw_slug: str) -> str:
        return Sanitizers.slug(raw_slug)


class ListedAnalysisPost(BaseListedPost[AnalysisMeta]):
    pass


class ListedArticlePost(BaseListedPost[ArticleMeta]):
    pass


class ListedHighPotentialPost(BaseListedPost[HighPotentialMeta]):
    pass
