from dataclasses import dataclass
from typing import Optional

@dataclass
class LostItemRemoval:
    id: Optional[str]
    item_id: str
    removed_by: str
    removed_at: str
    notes: str
    previous_status: str
