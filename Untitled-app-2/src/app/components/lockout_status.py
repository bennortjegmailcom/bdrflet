"""Human-readable lockout state labels for the workflow panel."""

from app.models.job_card import JobCard
from app.models.lockout import Lockout, LockoutState


_STATE_LABELS = {
    LockoutState.NONE: "NO LOCKOUT REQUEST",
    LockoutState.REQUESTED: "LOCKOUT REQUESTED",
    LockoutState.EQUIPMENT_CONFIRMED: "EQUIPMENT CONFIRMED",
    LockoutState.SCADA_STOP_CONFIRMED: "SCADA STOP CONFIRMED",
    LockoutState.LOCKOUT_ACTIVE: "LOCKOUT ACTIVE",
    LockoutState.REJECTED: "LOCKOUT REJECTED",
    LockoutState.RELEASE_REQUESTED: "RELEASE REQUESTED",
    LockoutState.RELEASED: "RELEASED",
}


def lockout_state_for(job: JobCard, record: Lockout | None) -> LockoutState:
    if record is not None:
        return record.status
    try:
        return LockoutState(job.lockout_status)
    except ValueError:
        return LockoutState.NONE


def lockout_state_label(state: LockoutState) -> str:
    return _STATE_LABELS[state]
