from typing import Any
from pydantic import BaseModel


class EditorJsBlock(BaseModel):
    type: str
    data: dict[str, Any]


class EditorJsBody(BaseModel):
    time: int
    version: str
    blocks: list[EditorJsBlock]


class ArticleContent(BaseModel):
    body: EditorJsBody


class AnalysisContent(BaseModel):
    body: EditorJsBody
    updates: list[EditorJsBody] | None = None
