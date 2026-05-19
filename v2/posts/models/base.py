from typing import Literal, TypeVar


PostType = Literal["analysis", "blog", "news", "high-potential"]
PostStatus = Literal["published", "draft", "archived"]
HighPotentialCategory = Literal["bronze", "silver", "gold"]

ValidPostTypes = set(PostType.__args__)
ValidPostStatuses = set(PostStatus.__args__)

TMeta = TypeVar("TMeta")
TContent = TypeVar("TContent")
