from pydantic import BaseModel
from typing import List, Optional


class Option(BaseModel):
    name: str
    category: str


class CodeResponse(BaseModel):
    code: Optional[str]


class Match(BaseModel):
    chain: List[str]
    code: str
    category: str


class UnitOption(BaseModel):
    name: str
    category: str
    code: str


class HierarchyOption(BaseModel):
    name: str
    category: str
    code: Optional[str] = None


class CodeSearchResult(BaseModel):
    code: str
    ua_code: str
    chain: List[str]
    category: str
    category_label: str
