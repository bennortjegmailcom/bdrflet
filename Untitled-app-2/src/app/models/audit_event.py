from dataclasses import dataclass


@dataclass(frozen=True)
class AuditEvent:
    """Immutable audit record; services expose append and query, never edit/delete."""

    event_id: str
    job_card_id: str
    lockout_id: str | None
    event_type: str
    previous_state: str
    new_state: str
    user: str
    timestamp: str
    equipment: str
    reason: str = ""
