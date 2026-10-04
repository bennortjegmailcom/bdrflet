"""Append-only application audit log. Production storage belongs behind this boundary."""

from datetime import datetime
from uuid import uuid4

from app.models.audit_event import AuditEvent


class AuditService:
    def __init__(self, notification_service=None):
        self._events: list[AuditEvent] = []
        self._notification_service = notification_service
        self._seeded = False

    async def record(
        self,
        *,
        job_card_id: str,
        event_type: str,
        user: str,
        equipment: str = "",
        lockout_id: str | None = None,
        previous_state: str = "",
        new_state: str = "",
        reason: str = "",
        timestamp: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=f"AUD-{uuid4().hex[:12].upper()}",
            job_card_id=job_card_id,
            lockout_id=lockout_id,
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state,
            user=user,
            timestamp=timestamp or datetime.now().astimezone().isoformat(timespec="seconds"),
            equipment=equipment,
            reason=reason,
        )
        self._events.append(event)
        if self._notification_service is not None:
            await self._notification_service.from_audit_event(event)
        return event

    async def seed_demo_history(self, job_cards, reports) -> None:
        if self._seeded:
            return
        self._seeded = True
        report_by_id = {report.reference: report for report in reports}
        for card in job_cards:
            report = report_by_id.get(card.report_id)
            await self.record(
                job_card_id=card.job_card_id,
                event_type="REPORT_CREATED",
                user="Riley Morgan",
                equipment=card.equipment,
                new_state="New",
                timestamp=getattr(report, "created_at", ""),
            )
            await self.record(
                job_card_id=card.job_card_id,
                event_type="JOB_ASSIGNED" if card.assigned_worker != "Unassigned" else "JOB_CREATED",
                user="BDR demo system",
                equipment=card.equipment,
                previous_state="OPEN",
                new_state=card.status,
                timestamp=card.updated_at or card.created_at,
            )

    async def get_events(self, job_card_id: str | None = None) -> tuple[AuditEvent, ...]:
        events = self._events
        if job_card_id is not None:
            events = [event for event in events if event.job_card_id == job_card_id]
        return tuple(events)
