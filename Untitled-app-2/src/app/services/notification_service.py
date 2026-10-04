"""Notification facade with a replaceable provider and local read-state support."""

from datetime import datetime
from uuid import uuid4

from app.models.work_items import BdrNotification

_EVENT_COPY = {
    "JOB_ASSIGNED": ("Job assigned", "A job card has been assigned to you."),
    "LOCKOUT_REQUESTED": ("Lockout requested", "An authorised confirmation workflow is required."),
    "EQUIPMENT_CONFIRMED": ("SCADA confirmation required", "Equipment was confirmed; record the SCADA stop confirmation."),
    "SCADA_STOP_CONFIRMED": ("Physical lockout confirmation required", "Record the physical isolation confirmation."),
    "LOCKOUT_REJECTED": ("Lockout rejected", "A lockout workflow step was rejected."),
    "LOCKOUT_ACTIVE": ("Lockout active", "The authorised lockout sequence is complete."),
    "LOCKOUT_RELEASE_REQUESTED": ("Release requested", "An authorised release confirmation is required."),
    "LOCKOUT_RELEASE_APPROVED": ("Lockout released", "The authorised release was recorded."),
    "JOB_UPDATED": ("Job updated", "A job card has new work notes or status."),
}


class NotificationService:
    def __init__(self, local_store=None):
        self._items: list[BdrNotification] = [
            BdrNotification("Job card assigned", "JC-3908 is waiting for your attention.", "42 min ago", True,
                            "NTF-DEMO-1", "JOB_ASSIGNED", "JC-3908"),
            BdrNotification("Report updated", "BR-2476 moved to In review.", "2 hr ago", False,
                            "NTF-DEMO-2", "JOB_UPDATED", "JC-3891"),
        ]
        self._local_store = local_store

    async def get_notifications(self) -> tuple[BdrNotification, ...]:
        return tuple(self._items)

    @property
    def unread_count(self) -> int:
        return sum(item.unread for item in self._items)

    async def mark_read(self, notification_id: str) -> None:
        self._items = [
            BdrNotification(item.title, item.message, item.age, False, item.notification_id,
                            item.kind, item.job_card_id, item.event_id)
            if item.notification_id == notification_id else item
            for item in self._items
        ]
        if self._local_store is not None:
            await self._local_store.set_notification_read(notification_id, True)

    async def from_audit_event(self, event) -> None:
        title, message = _EVENT_COPY.get(event.event_type, ("Job updated", "A job card workflow has changed."))
        if event.event_type in {"REPORT_CREATED", "JOB_CREATED"}:
            return
        timestamp = event.timestamp or datetime.now().astimezone().isoformat(timespec="minutes")
        self._items.insert(
            0,
            BdrNotification(
                title=title,
                message=f"{message} · {event.job_card_id}",
                age=timestamp,
                unread=True,
                notification_id=f"NTF-{uuid4().hex[:12].upper()}",
                kind=event.event_type,
                job_card_id=event.job_card_id,
                event_id=event.event_id,
            ),
        )
