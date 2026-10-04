"""Local persistence abstraction: SQLite on devices and preferences in web preview."""

import json
import os
import sqlite3
from typing import Any


class LocalDatabase:
    async def put(self, collection: str, key: str, value: Any) -> None:
        raise NotImplementedError

    async def get(self, collection: str, key: str) -> Any | None:
        raise NotImplementedError

    async def values(self, collection: str) -> list[Any]:
        raise NotImplementedError

    async def remove(self, collection: str, key: str) -> None:
        raise NotImplementedError

    async def queue_operation(self, operation_id: str, operation_type: str, payload: dict) -> None:
        operation_type = operation_type.strip().casefold()
        if "lockout" in operation_type or payload.get("new_state") == "LOCKOUT_ACTIVE":
            raise ValueError("Lockout transitions cannot be queued for offline authority.")
        await self.put("pending_api_operations", operation_id,
                       {"operation_type": operation_type, "payload": payload})

    async def save_draft_report(self, draft_id: str, draft: dict) -> None:
        await self.put("draft_reports", draft_id, draft)

    async def save_pending_attachment(self, attachment_id: str, attachment: dict) -> None:
        await self.put("pending_attachments", attachment_id, attachment)

    async def cache_equipment(self, equipment_id: str, equipment: dict) -> None:
        await self.put("cached_equipment", equipment_id, equipment)

    async def cache_job_card(self, job_card_id: str, job_card: dict) -> None:
        await self.put("cached_job_cards", job_card_id, job_card)

    async def set_notification_read(self, notification_id: str, read: bool) -> None:
        await self.put("notification_state", notification_id, {"read": read})


class SQLiteLocalDatabase(LocalDatabase):
    """Small key/value repository over SQLite; app services own all access."""

    def __init__(self, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self._connection = sqlite3.connect(filename)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS local_records (collection TEXT NOT NULL, record_key TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(collection, record_key))"
        )
        self._connection.commit()

    async def put(self, collection: str, key: str, value: Any) -> None:
        payload = json.dumps(value, default=_json_default)
        self._connection.execute(
            "INSERT INTO local_records(collection, record_key, payload) VALUES (?, ?, ?) "
            "ON CONFLICT(collection, record_key) DO UPDATE SET payload=excluded.payload",
            (collection, key, payload),
        )
        self._connection.commit()

    async def get(self, collection: str, key: str) -> Any | None:
        row = self._connection.execute(
            "SELECT payload FROM local_records WHERE collection=? AND record_key=?",
            (collection, key),
        ).fetchone()
        return json.loads(row[0]) if row else None

    async def values(self, collection: str) -> list[Any]:
        rows = self._connection.execute(
            "SELECT payload FROM local_records WHERE collection=? ORDER BY rowid", (collection,)
        ).fetchall()
        return [json.loads(row[0]) for row in rows]

    async def remove(self, collection: str, key: str) -> None:
        self._connection.execute(
            "DELETE FROM local_records WHERE collection=? AND record_key=?", (collection, key)
        )
        self._connection.commit()


class PreferencesLocalDatabase(LocalDatabase):
    """Browser-preview fallback, where a native SQLite file is unavailable."""

    PREFIX = "bdr_local:"

    def __init__(self, preferences):
        self._preferences = preferences

    def _key(self, collection: str, key: str) -> str:
        return f"{self.PREFIX}{collection}:{key}"

    async def put(self, collection: str, key: str, value: Any) -> None:
        await self._preferences.set(self._key(collection, key), json.dumps(value, default=_json_default))

    async def get(self, collection: str, key: str) -> Any | None:
        raw = await self._preferences.get(self._key(collection, key))
        return json.loads(raw) if isinstance(raw, str) else None

    async def values(self, collection: str) -> list[Any]:
        prefix = f"{self.PREFIX}{collection}:"
        keys = await self._preferences.get_keys(prefix)
        result = []
        for key in keys:
            raw = await self._preferences.get(key)
            if isinstance(raw, str):
                result.append(json.loads(raw))
        return result

    async def remove(self, collection: str, key: str) -> None:
        await self._preferences.remove(self._key(collection, key))


def _json_default(value):
    if isinstance(value, bytes):
        return {"__bytes__": list(value)}
    if hasattr(value, "__dict__"):
        return value.__dict__
    return str(value)
