"""Job card service facade and API provider contract."""

from typing import Protocol

from app.models.job_card import JobCard


class JobCardApiProvider(Protocol):
    async def get_job_cards(self) -> tuple[JobCard, ...]:
        """Return job cards available to the signed-in user."""

    async def get_job_card(self, job_card_id: str) -> JobCard | None:
        """Return one authorized job card."""

    async def add_job_note(self, job_card_id: str, note: str) -> JobCard | None:
        """Append a work note and return the updated card."""


class JobCardService:
    def __init__(self, provider: JobCardApiProvider, audit_service=None):
        self._provider = provider
        self._audit_service = audit_service

    async def get_job_cards(self) -> tuple[JobCard, ...]:
        return await self._provider.get_job_cards()

    async def get_job_card(self, job_card_id: str) -> JobCard | None:
        return await self._provider.get_job_card(job_card_id)

    async def add_work_note(self, job_card_id: str, note: str, user=None) -> JobCard | None:
        note = note.strip()
        if not note:
            raise ValueError("Work note cannot be empty.")
        updated = await self._provider.add_job_note(job_card_id, note)
        if updated is not None and self._audit_service is not None:
            await self._audit_service.record(
                job_card_id=job_card_id,
                event_type="JOB_UPDATED",
                user=user.name if user is not None else "Current user",
                equipment=updated.equipment,
                previous_state=updated.status,
                new_state=updated.status,
                reason="Work note added",
            )
        return updated
