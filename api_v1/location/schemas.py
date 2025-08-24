from pydantic import BaseModel, Field
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


class Provider(BaseModel):
    name: str
    service: str
    license: str


class Order(BaseModel):
    title: str
    number: str
    date: str
    pdf_url: str


class Credit(BaseModel):
    provider: Provider
    order: Order


class SearchResponse(BaseModel):
    credit: Credit
    data: List[Match] = Field(..., description="List of found matches")


class HierarchyResponse(BaseModel):
    credit: dict
    data: List[HierarchyOption]

    class Config:
        schema_extra = {
            "example": {
                "credit": {
                    "provider": {
                        "name": "Example Provider",
                        "service": "Example Service",
                        "license": "Example License",
                    },
                    "order": {
                        "title": "Example Order",
                        "number": "1234",
                        "date": "2025-01-01",
                        "pdf_url": "https://example.com/order.pdf",
                    },
                },
                "data": [
                    {
                        "name": "Example Name",
                        "category": "Example Category",
                        "code": "UA00000000000000000",
                    }
                ],
            }
        }


class CodeSearchResponse(BaseModel):
    credit: dict
    data: CodeSearchResult
