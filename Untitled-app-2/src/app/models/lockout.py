"""Lockout workflow states and immutable audit records."""

from dataclasses import dataclass
from enum import Enum


class LockoutState(str, Enum):
    NONE = "NONE"
    REQUESTED = "REQUESTED"
    EQUIPMENT_CONFIRMED = "EQUIPMENT_CONFIRMED"
    SCADA_STOP_CONFIRMED = "SCADA_STOP_CONFIRMED"
    LOCKOUT_ACTIVE = "LOCKOUT_ACTIVE"
    REJECTED = "REJECTED"
    RELEASE_REQUESTED = "RELEASE_REQUESTED"
    RELEASED = "RELEASED"


@dataclass(frozen=True)
class LockoutAuditEvent:
    user_id: str
    user_name: str
    timestamp: str
    equipment_id: str
    job_card_id: str
    lockout_id: str
    previous_state: LockoutState
    new_state: LockoutState
    action: str
    reason: str = ""


@dataclass(frozen=True)
class Lockout:
    lockout_id: str
    job_card_id: str
    equipment_id: str
    requested_by: str
    requested_at: str
    status: LockoutState
    reason: str = ""
    requested_by_name: str = ""
    equipment_confirmed_by: str = ""
    equipment_confirmed_at: str = ""
    scada_stop_confirmed_by: str = ""
    scada_stop_confirmed_at: str = ""
    physical_lockout_confirmed_by: str = ""
    physical_lockout_confirmed_at: str = ""
    rejection_reason: str = ""
    release_requested_by: str = ""
    release_requested_by_name: str = ""
    release_requested_at: str = ""
    release_request_reason: str = ""
    released_by: str = ""
    released_at: str = ""
    released_by_name: str = ""
    release_approval_reason: str = ""
    audit_trail: tuple[LockoutAuditEvent, ...] = ()
