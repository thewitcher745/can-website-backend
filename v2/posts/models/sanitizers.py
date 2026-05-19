import copy
from datetime import datetime
import re
from typing import Any, cast

from .base import HighPotentialCategory


class Sanitizers:
    @staticmethod
    def strip(raw_str: str) -> str:
        """Just strips the string. Used for titles, descriptions, etc."""
        return raw_str.strip()

    @staticmethod
    def symbol(raw_symbol: str) -> str:
        """
        Removes symbols (? ! # - _, except .) from a coin's symbol and uppercases it.
        """
        symbol = raw_symbol.upper().replace("USDT", "").replace("USD", "")
        symbol = re.sub(r"[^A-Za-z0-9.]", "", symbol)
        symbol = symbol.strip().strip(".")

        return symbol

    @staticmethod
    def tag(raw_tag: str) -> str:
        """
        Strips whitespaces from tag.
        """

        return raw_tag.strip()

    @staticmethod
    def category(raw_category: str) -> HighPotentialCategory:
        """
        Strips and lowercases the category.
        """
        return cast(HighPotentialCategory, raw_category.strip().lower())

    @staticmethod
    def slug(raw_slug: str) -> str:
        """
        Sanitizes the slug. Lowercase, spaces replaced by dashes, no filename-breaking
        symbols (replaced by dashes), no trailing and leading symbols (including
        dashes), and no multiple dashes.
        """
        slug = raw_slug.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")

        return slug

    @staticmethod
    def datetime(value: str | datetime | None) -> datetime | None:
        """
        If input is a string, sanitizes it to isoformat datetime.
        Returns None if input is None.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    @staticmethod
    def sanitize_meta_dict(meta_dict: dict[str, Any]) -> dict[str, Any]:
        """Returns the sanitized version of a meta dict of any type."""
        sanitized_meta_dict = copy.deepcopy(meta_dict)

        for field in list(sanitized_meta_dict.keys()):
            if field in [
                "last_modified_at",
                "created_at",
                "published_at",
            ]:
                sanitized_meta_dict[field] = Sanitizers.datetime(
                    sanitized_meta_dict[field]
                )

            if field == "coins":
                sanitized_meta_dict[field] = [
                    Sanitizers.symbol(coin) for coin in sanitized_meta_dict[field]
                ]

            elif field == "tags":
                sanitized_meta_dict[field] = [
                    Sanitizers.tag(tag) for tag in sanitized_meta_dict[field]
                ]

            elif field == "category":
                sanitized_meta_dict[field] = Sanitizers.category(
                    sanitized_meta_dict[field]
                )

            elif field in ["title", "description", "author"]:
                sanitized_meta_dict[field] = Sanitizers.strip(
                    sanitized_meta_dict[field]
                )

        return sanitized_meta_dict
