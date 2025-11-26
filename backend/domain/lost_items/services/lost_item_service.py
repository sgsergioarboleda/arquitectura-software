from datetime import datetime
from domain.lost_items.models.lost_item import LostItem
from domain.lost_items.models.lost_item_removal import LostItemRemoval

class LostItemService:
    def __init__(self, lost_repo, removal_repo):
        self.lost_repo = lost_repo
        self.removal_repo = removal_repo

    def remove_item(self, item_id: str, removed_by: str, notes: str):
        item = self.lost_repo.find_by_id(item_id)
        if not item:
            raise ValueError("Objeto no encontrado")

        if item.status == "removed":
            raise ValueError("El objeto ya fue removido")

        removal = LostItemRemoval(
            id=None,
            item_id=item_id,
            removed_by=removed_by,
            removed_at=datetime.now().isoformat(),
            notes=notes,
            previous_status=item.status
        )

        saved_removal = self.removal_repo.save_removal(removal)

        item.status = "removed"
        item.updated_at = datetime.now().isoformat()
        item.removal_id = saved_removal.id

        updated = self.lost_repo.update(item)

        return {
            "message": "Objeto removido exitosamente",
            "item_id": item_id,
            "removal_id": saved_removal.id,
            "removed_at": saved_removal.removed_at
        }
