"""Conservative offline queue foundation; lockout operations are never synchronized here."""

from uuid import uuid4

from app.services.connectivity_service import ConnectivityService, ConnectivityStatus


class SyncService:
    def __init__(self, storage, connectivity: ConnectivityService, transport=None):
        self._storage = storage
        self._connectivity = connectivity
        self._transport = transport

    async def save_draft_report(self, draft: dict) -> str:
        draft_id = f"DRAFT-{uuid4().hex[:12].upper()}"
        await self._storage.save_draft_report(draft_id, draft)
        return draft_id

    async def queue_operation(self, operation_type: str, payload: dict) -> str:
        operation_id = f"OP-{uuid4().hex[:12].upper()}"
        await self._storage.queue_operation(operation_id, operation_type, payload)
        return operation_id

    async def synchronize(self) -> int:
        if self._connectivity.status == ConnectivityStatus.OFFLINE:
            return 0
        pending = await self._storage.values("pending_api_operations")
        if not pending:
            await self._connectivity.sync_finished()
            return 0
        if self._transport is None:
            await self._connectivity.sync_failed(
                "BDR API is not connected; pending operations were retained locally."
            )
            return 0
        await self._connectivity.begin_sync()
        try:
            completed = await self._transport.send(pending)
        except Exception as exc:
            await self._connectivity.sync_failed(str(exc))
            return 0
        for item in completed:
            await self._storage.remove("pending_api_operations", item["operation_id"])
        await self._connectivity.sync_finished()
        return len(completed)

    async def cache_records(self, collection: str, records: list[tuple[str, dict]]) -> None:
        if collection not in {"cached_equipment", "cached_job_cards"}:
            raise ValueError("Only equipment and job card records can be cached here.")
        for key, value in records:
            await self._storage.put(collection, key, value)
