from datetime import datetime
from typing import Annotated
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
)
from pydantic_core import PydanticCustomError

from .base import HighPotentialCategory
from .sanitizers import Sanitizers


def to_camel(name: str) -> str:
    # snake_case → camelCase for output
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


MIN_TAG_LENGTH = 1
MAX_TAG_LENGTH = 30
MIN_N_TAGS = 1
MAX_N_TAGS = 20

MIN_COIN_LENGTH = 1
MAX_COIN_LENGTH = 20
MIN_N_COINS = 1
MAX_N_COINS = 10

WhitespaceStrippedString = Annotated[str, StringConstraints(strip_whitespace=True)]


class BaseMeta(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: Annotated[
        WhitespaceStrippedString, StringConstraints(min_length=1, max_length=200)
    ]
    author: Annotated[
        WhitespaceStrippedString, StringConstraints(min_length=1, max_length=50)
    ]
    published_at: datetime | None = None
    last_modified_at: datetime | None = None
    created_at: datetime | None = None
    description: Annotated[
        WhitespaceStrippedString, StringConstraints(min_length=1, max_length=1000)
    ]
    tags: list[str] = Field(max_length=MAX_N_TAGS)

    @field_validator("published_at", "last_modified_at", "created_at", mode="before")
    @classmethod
    def sanitize_datetimes(cls, raw_datetime: datetime | str | None) -> datetime | None:
        return Sanitizers.datetime(raw_datetime)

    @field_validator("tags", mode="before")
    @classmethod
    def sanitize_tags(cls, raw_tags: list[str]) -> list[str]:
        # Sanitize each individual tag
        cleaned = [Sanitizers.tag(t) for t in raw_tags]

        # Deduplicate while preserving order
        return list(dict.fromkeys(cleaned))

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, raw_tags: list[str]) -> list[str]:
        for tag in raw_tags:
            # Ensure each tag has valid length
            if not (MIN_TAG_LENGTH <= len(tag) <= MAX_TAG_LENGTH):
                raise PydanticCustomError(
                    "invalid_tag",
                    "Tag '{tag}' is invalid: must be {min_length}-{max_length} characters",
                    {
                        "tag": tag,
                        "min_length": MIN_TAG_LENGTH,
                        "max_length": MAX_TAG_LENGTH,
                    },
                )

        return raw_tags


class ArticleMeta(BaseMeta):
    thumbnail: HttpUrl


class AnalysisMeta(BaseMeta):
    coins: list[str] = Field(min_length=1, max_length=10)
    image: HttpUrl
    is_vip: bool

    @field_validator("coins", mode="before")
    @classmethod
    def sanitize_coins(cls, raw_coins: list[str]) -> list[str]:
        # Sanitize each coin
        cleaned = [Sanitizers.symbol(c) for c in raw_coins]

        # Deduplicate while preserving order
        return list(dict.fromkeys(cleaned))

    @field_validator("coins")
    @classmethod
    def validate_coins(cls, raw_coins: list[str]) -> list[str]:
        for coin in raw_coins:
            # Ensure each coin has valid length
            if not (MIN_TAG_LENGTH <= len(coin) <= MAX_TAG_LENGTH):
                raise PydanticCustomError(
                    "invalid_coin",
                    "Coin '{coin}' is invalid: must be {min_length}-{max_length} characters",
                    {
                        "coin": coin,
                        "min_length": MIN_TAG_LENGTH,
                        "max_length": MAX_TAG_LENGTH,
                    },
                )

        return raw_coins


class HighPotentialMeta(BaseMeta):
    image: HttpUrl
    logo: HttpUrl
    symbol: str = Field(min_length=1, max_length=20)
    category: HighPotentialCategory

    @field_validator("symbol", mode="before")
    @classmethod
    def sanitize_symbol(cls, raw_symbol: str) -> str:
        return Sanitizers.symbol(raw_symbol)

    @field_validator("category", mode="before")
    @classmethod
    def sanitize_category(cls, raw_category: str) -> HighPotentialCategory:
        return Sanitizers.category(raw_category)


PostMeta = ArticleMeta | AnalysisMeta | HighPotentialMeta
