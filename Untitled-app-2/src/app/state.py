from dataclasses import dataclass, field

from app.models.dashboard import DashboardSummary
from app.models.user import User
from app.models.job_card import JobCard
from app.models.lockout import Lockout
from app.models.positive_test import PositiveTest
from app.models.work_items import BdrNotification, BreakdownReport
from app.services.auth_service import AuthService
from app.services.bdr_service import BdrService
from app.services.permission_service import PermissionService
from app.services.report_service import ReportService
from app.services.job_card_service import JobCardService
from app.services.equipment_service import EquipmentService
from app.services.equipment_identification_service import EquipmentIdentificationService
from app.services.lockout_service import LockoutService
from app.services.positive_test_service import PositiveTestService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.connectivity_service import ConnectivityService
from app.services.sync_service import SyncService
from app.storage.local_database import LocalDatabase
from app.models.audit_event import AuditEvent


@dataclass
class AppState:
    service: BdrService
    auth_service: AuthService
    report_service: ReportService
    job_card_service: JobCardService
    equipment_service: EquipmentService
    equipment_identification_service: EquipmentIdentificationService
    lockout_service: LockoutService
    positive_test_service: PositiveTestService
    audit_service: AuditService | None = None
    notification_service: NotificationService | None = None
    connectivity_service: ConnectivityService = field(default_factory=ConnectivityService)
    local_database: LocalDatabase | None = None
    sync_service: SyncService | None = None
    audit_events: tuple[AuditEvent, ...] = ()
    permission_service: PermissionService = field(default_factory=PermissionService)
    current_route: str = "/login"
    current_user: User | None = None
    dashboard: DashboardSummary | None = None
    reports: tuple[BreakdownReport, ...] = ()
    job_cards: tuple[JobCard, ...] = ()
    lockouts: dict[str, Lockout] = field(default_factory=dict)
    positive_tests: dict[str, tuple[PositiveTest, ...]] = field(default_factory=dict)
    notifications: tuple[BdrNotification, ...] = ()
    selected_report_id: str | None = None
    selected_job_card_id: str | None = None

    @property
    def unread_notification_count(self) -> int:
        return sum(item.unread for item in self.notifications)

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None and self.current_user.active

    @property
    def profile(self) -> User | None:
        """Compatibility alias for screens that previously read state.profile."""
        return self.current_user

    @property
    def demo_session(self) -> bool:
        """Compatibility alias for the previous in-memory demo session flag."""
        return self.is_authenticated

    def clear_session(self) -> None:
        self.current_user = None
        self.dashboard = None
        self.reports = ()
        self.job_cards = ()
        self.lockouts = {}
        self.positive_tests = {}
        self.notifications = ()
        self.selected_report_id = None
        self.selected_job_card_id = None

    def sign_out(self) -> None:
        """Clear local session state; authentication service logout is handled by the router."""
        self.clear_session()
