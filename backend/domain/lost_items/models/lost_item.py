from dataclasses import dataclass
from typing import Optional

@dataclass
class LostItem:
    id: Optional[str]
    title: str
    found_location: str
    status: str = "available"
    updated_at: Optional[str] = None
    removal_id: Optional[str] = None
