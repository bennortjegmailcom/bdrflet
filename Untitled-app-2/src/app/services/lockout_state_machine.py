"""Single source of truth for allowed lockout workflow transitions."""

from app.models.lockout import LockoutState


class InvalidLockoutTransition(ValueError):
    """Raised when a requested transition is not allowed by the workflow."""


_TRANSITIONS = {
    "request": {LockoutState.NONE: LockoutState.REQUESTED},
    "confirm_equipment": {LockoutState.REQUESTED: LockoutState.EQUIPMENT_CONFIRMED},
    "confirm_scada_stop": {LockoutState.EQUIPMENT_CONFIRMED: LockoutState.SCADA_STOP_CONFIRMED},
    "confirm_physical_lockout": {LockoutState.SCADA_STOP_CONFIRMED: LockoutState.LOCKOUT_ACTIVE},
    "reject": {
        LockoutState.REQUESTED: LockoutState.REJECTED,
        LockoutState.EQUIPMENT_CONFIRMED: LockoutState.REJECTED,
        LockoutState.SCADA_STOP_CONFIRMED: LockoutState.REJECTED,
    },
    "request_release": {LockoutState.LOCKOUT_ACTIVE: LockoutState.RELEASE_REQUESTED},
    "approve_release": {LockoutState.RELEASE_REQUESTED: LockoutState.RELEASED},
}


class LockoutStateMachine:
    """Validate state changes; callers cannot choose a destination state."""

    @staticmethod
    def transition(current: LockoutState, action: str) -> LockoutState:
        allowed = _TRANSITIONS.get(action)
        if allowed is None:
            raise InvalidLockoutTransition(f"Unknown lockout action: {action}.")
        destination = allowed.get(current)
        if destination is None:
            raise InvalidLockoutTransition(
                f"Cannot {action.replace('_', ' ')} while lockout is {current.value}."
            )
        return destination
