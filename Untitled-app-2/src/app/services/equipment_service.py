"""Equipment service facade for search, lookup, and QR resolution."""

from typing import Protocol

from app.models.equipment import Equipment


class EquipmentApiProvider(Protocol):
    async def search_equipment(self, query: str) -> tuple[Equipment, ...]:
        """Search equipment the signed-in user may select."""

    async def get_equipment(self, equipment_id: str) -> Equipment | None:
        """Resolve an equipment identifier or equipment code."""

    async def resolve_equipment_qr(self, qr_identifier: str) -> Equipment | None:
        """Resolve only a known active equipment QR identifier."""


class EquipmentService:
    def __init__(self, provider: EquipmentApiProvider):
        self._provider = provider

    async def search(self, query: str = "") -> tuple[Equipment, ...]:
        return await self._provider.search_equipment(query)

    async def get_by_id(self, equipment_id: str) -> Equipment | None:
        return await self._provider.get_equipment(equipment_id)

    async def resolve_qr(self, qr_identifier: str) -> Equipment | None:
        if not qr_identifier.strip():
            return None
        return await self._provider.resolve_equipment_qr(qr_identifier)
