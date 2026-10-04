"""Client-side role permission checks for hiding unauthorized UI actions.

Production APIs must independently authorize every operation. These local checks
only improve the mobile experience and are never a security boundary.
"""

from app.models.user import User

CREATE_REPORT = "create_report"
VIEW_REPORT = "view_report"
CREATE_JOB_CARD = "create_job_card"
UPDATE_JOB_CARD = "update_job_card"
REQUEST_LOCKOUT = "request_lockout"
CONFIRM_EQUIPMENT = "confirm_equipment"
CONFIRM_SCADA_STOP = "confirm_scada_stop"
CONFIRM_PHYSICAL_LOCKOUT = "confirm_physical_lockout"
START_POSITIVE_TEST = "start_positive_test"
REQUEST_LOCKOUT_RELEASE = "request_lockout_release"
APPROVE_LOCKOUT_RELEASE = "approve_lockout_release"
ADMINISTRATION = "administration"

ALL_PERMISSIONS = frozenset(
    {
        CREATE_REPORT, VIEW_REPORT, CREATE_JOB_CARD, UPDATE_JOB_CARD,
        REQUEST_LOCKOUT, CONFIRM_EQUIPMENT, CONFIRM_SCADA_STOP,
        CONFIRM_PHYSICAL_LOCKOUT, START_POSITIVE_TEST,
        REQUEST_LOCKOUT_RELEASE, APPROVE_LOCKOUT_RELEASE, ADMINISTRATION,
    }
)

_REPORTER = frozenset({CREATE_REPORT, VIEW_REPORT})
_SCHEDULER = frozenset({VIEW_REPORT, CREATE_JOB_CARD, UPDATE_JOB_CARD})
_COORDINATOR = frozenset({
    CREATE_REPORT, VIEW_REPORT, CREATE_JOB_CARD, UPDATE_JOB_CARD, REQUEST_LOCKOUT,
})
_ARTISAN = frozenset({VIEW_REPORT, UPDATE_JOB_CARD, REQUEST_LOCKOUT, REQUEST_LOCKOUT_RELEASE})
_SUPERVISOR = frozenset({
    CREATE_REPORT, VIEW_REPORT, CREATE_JOB_CARD, UPDATE_JOB_CARD,
    REQUEST_LOCKOUT, CONFIRM_EQUIPMENT, CONFIRM_SCADA_STOP,
    CONFIRM_PHYSICAL_LOCKOUT, START_POSITIVE_TEST, REQUEST_LOCKOUT_RELEASE,
})
_ADMIN = _SUPERVISOR | frozenset({APPROVE_LOCKOUT_RELEASE, ADMINISTRATION})
_ROLE_PERMISSIONS = {
    "reporter": _REPORTER,
    "scheduler": _SCHEDULER,
    "coordinator": _COORDINATOR,
    "maintenance shift foreman": _SUPERVISOR | frozenset({APPROVE_LOCKOUT_RELEASE}),
    "foreman": _SUPERVISOR | frozenset({APPROVE_LOCKOUT_RELEASE}),
    "artisan": _ARTISAN,
    "guest": frozenset({VIEW_REPORT}),
    "admin": _ADMIN,
    "administrator": _ADMIN,
    "maintenance supervisor": _SUPERVISOR | frozenset({APPROVE_LOCKOUT_RELEASE}),
}


class PermissionService:
    """Evaluate local UI permissions using the authenticated user's role.

    Roles come only from the authentication provider; this service has no role
    assignment API. Mock confirmation permissions are conservative and must be
    replaced or confirmed by authoritative server-side policy in production.
    """

    def permissions_for(self, user: User | None) -> frozenset[str]:
        if user is None or not user.active:
            return frozenset()
        return _ROLE_PERMISSIONS.get(user.role.strip().casefold(), frozenset())

    def has_permission(self, user: User | None, permission: str) -> bool:
        if permission not in ALL_PERMISSIONS:
            return False
        return permission in self.permissions_for(user)
