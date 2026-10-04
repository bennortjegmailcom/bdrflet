"""Lockout workflow facade over a replaceable API provider.

Mobile checks guide the sequence only. Production APIs must atomically repeat
all permissions, equipment matching, and state-transition checks server-side.
"""

from dataclasses import replace
from datetime import datetime
from typing import Protocol

from app.models.job_card import JobCard
from app.models.lockout import Lockout, LockoutAuditEvent, LockoutState
from app.models.user import User
from app.services.lockout_state_machine import LockoutStateMachine
from app.services.permission_service import (
    APPROVE_LOCKOUT_RELEASE,
    CONFIRM_EQUIPMENT,
    CONFIRM_PHYSICAL_LOCKOUT,
    CONFIRM_SCADA_STOP,
    REQUEST_LOCKOUT,
    REQUEST_LOCKOUT_RELEASE,
    PermissionService,
)


class LockoutApiProvider(Protocol):
    async def get_job_card(self, job_card_id: str) -> JobCard | None: ...

    async def get_lockout_for_job(self, job_card_id: str) -> Lockout | None: ...

    async def create_lockout(self, lockout: Lockout) -> Lockout: ...

    async def save_lockout(self, lockout: Lockout) -> Lockout: ...


class LockoutService:
    def __init__(self, provider: LockoutApiProvider, permissions: PermissionService, audit_service=None):
        self._provider = provider
        self._permissions = permissions
        self._audit_service = audit_service
        self._state_machine = LockoutStateMachine()

    async def get_for_job_card(self, job_card_id: str) -> Lockout | None:
        return await self._provider.get_lockout_for_job(job_card_id)

    async def request_lockout(self, job_card_id: str, user: User | None, reason: str) -> Lockout:
        self._require_permission(user, REQUEST_LOCKOUT)
        reason = reason.strip()
        if not reason:
            raise ValueError("A lockout request reason is required.")
        job = await self._get_job(job_card_id)
        existing = await self._provider.get_lockout_for_job(job_card_id)
        previous = existing.status if existing else LockoutState.NONE
        next_state = self._state_machine.transition(previous, "request")
        now = _now_label()
        lockout_id = f"LO-{job.job_card_id}"
        event = _audit_event(
            user, now, job, lockout_id, previous, next_state, "LOCKOUT_REQUESTED", reason
        )
        created = await self._provider.create_lockout(
            Lockout(
                lockout_id=lockout_id,
                job_card_id=job.job_card_id,
                equipment_id=job.equipment_id,
                requested_by=user.id,
                requested_by_name=user.name,
                requested_at=now,
                status=next_state,
                reason=reason,
                audit_trail=(event,),
            )
        )
        await self._record_audit(job, user, created, previous, next_state, "LOCKOUT_REQUESTED", reason, now)
        return created

    async def confirm_equipment(
        self, job_card_id: str, user: User | None, scanned_equipment_id: str
    ) -> Lockout:
        job = await self._get_job(job_card_id)
        scanned_equipment_id = scanned_equipment_id.strip()
        if not scanned_equipment_id or scanned_equipment_id.casefold() != job.equipment_id.casefold():
            raise ValueError("Equipment mismatch. Lockout cannot continue.")
        now = _now_label()
        return await self._apply(
            job_card_id, user, "confirm_equipment", CONFIRM_EQUIPMENT,
            "EQUIPMENT_CONFIRMED", "Equipment identity confirmed by matching QR scan.", now,
            equipment_confirmed_by=_actor_id(user), equipment_confirmed_at=now,
        )

    async def confirm_scada_stop(self, job_card_id: str, user: User | None) -> Lockout:
        now = _now_label()
        return await self._apply(
            job_card_id, user, "confirm_scada_stop", CONFIRM_SCADA_STOP,
            "SCADA_STOP_CONFIRMED", "Authorised user confirmed per approved site procedure.", now,
            scada_stop_confirmed_by=_actor_id(user), scada_stop_confirmed_at=now,
        )

    async def confirm_physical_lockout(self, job_card_id: str, user: User | None) -> Lockout:
        now = _now_label()
        return await self._apply(
            job_card_id, user, "confirm_physical_lockout", CONFIRM_PHYSICAL_LOCKOUT,
            "PHYSICAL_LOCKOUT_CONFIRMED", "Authorised user confirmed physical isolation in person.", now,
            physical_lockout_confirmed_by=_actor_id(user), physical_lockout_confirmed_at=now,
        )

    async def reject(self, job_card_id: str, user: User | None, reason: str) -> Lockout:
        reason = reason.strip()
        if not reason:
            raise ValueError("A rejection reason is required.")
        record = await self._provider.get_lockout_for_job(job_card_id)
        if record is None:
            raise ValueError("No lockout request exists for this job card.")
        permission, action_label = {
            LockoutState.REQUESTED: (CONFIRM_EQUIPMENT, "EQUIPMENT_REJECTED"),
            LockoutState.EQUIPMENT_CONFIRMED: (CONFIRM_SCADA_STOP, "SCADA_STOP_NOT_CONFIRMED"),
            LockoutState.SCADA_STOP_CONFIRMED: (CONFIRM_PHYSICAL_LOCKOUT, "PHYSICAL_LOCKOUT_REJECTED"),
        }.get(record.status, (None, "LOCKOUT_REJECTED"))
        if permission is None:
            raise ValueError(f"Cannot reject while lockout is {record.status.value}.")
        now = _now_label()
        return await self._apply(
            job_card_id, user, "reject", permission, action_label, reason, now,
            rejection_reason=reason,
        )

    async def request_release(
        self, job_card_id: str, user: User | None, reason: str
    ) -> Lockout:
        reason = reason.strip()
        if not reason:
            raise ValueError("A lockout release reason is required.")
        now = _now_label()
        return await self._apply(
            job_card_id, user, "request_release", REQUEST_LOCKOUT_RELEASE,
            "LOCKOUT_RELEASE_REQUESTED", reason, now,
            release_requested_by=_actor_id(user),
            release_requested_by_name=user.name if user else "",
            release_requested_at=now,
            release_request_reason=reason,
        )

    async def approve_release(
        self, job_card_id: str, user: User | None, reason: str = ""
    ) -> Lockout:
        now = _now_label()
        return await self._apply(
            job_card_id, user, "approve_release", APPROVE_LOCKOUT_RELEASE,
            "LOCKOUT_RELEASE_APPROVED", reason.strip(), now,
            released_by=_actor_id(user), released_at=now,
            released_by_name=user.name if user else "",
            release_approval_reason=reason.strip(),
        )

    async def _apply(
        self,
        job_card_id: str,
        user: User | None,
        transition: str,
        permission: str,
        action: str,
        reason: str,
        timestamp: str,
        **fields: str,
    ) -> Lockout:
        self._require_permission(user, permission)
        job = await self._get_job(job_card_id)
        record = await self._provider.get_lockout_for_job(job_card_id)
        if record is None:
            raise ValueError("No lockout request exists for this job card.")
        if record.equipment_id.casefold() != job.equipment_id.casefold():
            raise ValueError("Equipment mismatch. Lockout cannot continue.")
        previous = record.status
        next_state = self._state_machine.transition(previous, transition)
        event = _audit_event(
            user, timestamp, job, record.lockout_id, previous, next_state, action, reason
        )
        updated = replace(
            record,
            status=next_state,
            audit_trail=(*record.audit_trail, event),
            **fields,
        )
        saved = await self._provider.save_lockout(updated)
        await self._record_audit(job, user, saved, previous, next_state, action, reason, timestamp)
        return saved

    async def _record_audit(self, job, user, lockout, previous, new, action, reason, timestamp):
        if self._audit_service is not None:
            await self._audit_service.record(
                job_card_id=job.job_card_id,
                lockout_id=lockout.lockout_id,
                event_type=action,
                previous_state=previous.value,
                new_state=new.value,
                user=user.name if user is not None else "Unknown user",
                timestamp=timestamp,
                equipment=job.equipment,
                reason=reason,
            )

    async def _get_job(self, job_card_id: str) -> JobCard:
        job = await self._provider.get_job_card(job_card_id)
        if job is None:
            raise ValueError("Job card is no longer available.")
        if not job.equipment_id:
            raise ValueError("Lockout requires a job card linked to equipment.")
        return job

    def _require_permission(self, user: User | None, permission: str) -> None:
        if not self._permissions.has_permission(user, permission):
            raise PermissionError("Your role is not authorised to perform this lockout action.")


def _actor_id(user: User | None) -> str:
    if user is None:
        raise PermissionError("Sign in before performing a lockout action.")
    return user.id


def _audit_event(
    user: User | None,
    timestamp: str,
    job: JobCard,
    lockout_id: str,
    previous: LockoutState,
    new: LockoutState,
    action: str,
    reason: str,
) -> LockoutAuditEvent:
    if user is None:
        raise PermissionError("Sign in before performing a lockout action.")
    return LockoutAuditEvent(
        user_id=user.id,
        user_name=user.name,
        timestamp=timestamp,
        equipment_id=job.equipment_id,
        job_card_id=job.job_card_id,
        lockout_id=lockout_id,
        previous_state=previous,
        new_state=new,
        action=action,
        reason=reason,
    )


def _now_label() -> str:
    return datetime.now().strftime("%d %b %Y · %H:%M")
