"""Navigation access derived from the central permission service."""

from app.models.user import User
from app.services.permission_service import (
    CREATE_REPORT,
    CREATE_JOB_CARD,
    UPDATE_JOB_CARD,
    VIEW_REPORT,
    PermissionService,
)

HOME = "/home"
REPORTS = "/reports"
JOB_CARDS = "/job-cards"
NOTIFICATIONS = "/notifications"
PROFILE = "/profile"
CREATE_REPORT_ROUTE = "/create-report"
REPORT_DETAIL = "/report-detail"
JOB_CARD_DETAIL = "/job-card-detail"


def allowed_routes_for(
    user: User | None,
    permission_service: PermissionService | None = None,
) -> frozenset[str]:
    if user is None or not user.active:
        return frozenset()
    permissions = permission_service or PermissionService()
    routes = {HOME, NOTIFICATIONS, PROFILE}
    if permissions.has_permission(user, CREATE_REPORT):
        routes.add(CREATE_REPORT_ROUTE)
    if permissions.has_permission(user, VIEW_REPORT):
        routes.update({REPORTS, REPORT_DETAIL})
    if permissions.has_permission(user, CREATE_JOB_CARD) or permissions.has_permission(user, UPDATE_JOB_CARD):
        routes.update({JOB_CARDS, JOB_CARD_DETAIL})
    return frozenset(routes)


def can_access_route(
    user: User | None,
    route: str,
    permission_service: PermissionService | None = None,
) -> bool:
    return route in allowed_routes_for(user, permission_service)
