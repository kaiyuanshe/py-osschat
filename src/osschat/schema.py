from __future__ import annotations


from typing import Optional, List, Union, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Document:
    content: str
    id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FAQDocument(Document):
    answer: Optional[str] = None


@dataclass
class SematicSearchResult:
    result: str
    score: str
    meta: Dict[str, Any] = field(default_factory=dict)
