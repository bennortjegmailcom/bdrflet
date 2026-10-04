import asyncio
import logging

import flet as ft

LOGIN = "/login"
HOME = "/home"
REPORTS = "/reports"
JOB_CARDS = "/job-cards"
NOTIFICATIONS = "/notifications"
PROFILE = "/profile"
CREATE_REPORT_ROUTE = "/create-report"
REPORT_DETAIL = "/report-detail"
JOB_CARD_DETAIL = "/job-card-detail"

from app.components.feedback_states import error_state, loading_indicator
from app.models.user import User
from app.permissions import can_access_route
from app.screens.create_report_screen import build_create_report_screen
from app.screens.job_card_detail import build_job_card_detail_screen
from app.screens.home import build_home_screen
from app.screens.job_cards import build_job_cards_screen
from app.screens.login import build_login_screen
from app.screens.notifications import build_notifications_screen
from app.screens.profile import build_profile_screen
from app.screens.reports import build_reports_screen
from app.screens.report_detail import build_report_detail_screen
from app.state import AppState

log = logging.getLogger("app.routes")


class AppRouter:
    """Route manager that delegates authentication to the injected service."""

    def __init__(self, page: ft.Page, state: AppState, file_picker: ft.FilePicker):
        self.page = page
        self.state = state
        self.file_picker = file_picker

    async def initialize(self) -> None:
        try:
            user = await self.state.auth_service.refresh_session()
            if user is None or not user.active or not await self.state.auth_service.is_authenticated():
                self.state.clear_session()
                self._render(LOGIN)
                return
            self.state.current_user = await self.state.auth_service.get_current_user()
            if not self.state.is_authenticated:
                self.state.clear_session()
                self._render(LOGIN)
                return
            if await self._load_workspace(self.initialize):
                self._render(HOME)
        except Exception as exc:
            log.exception("Could not restore authentication session")
            self._show_error(exc, self.initialize)

    async def enter_demo(self) -> None:
        try:
            user: User | None = await self.state.auth_service.login()
            if user is None or not user.active or not await self.state.auth_service.is_authenticated():
                self.state.clear_session()
                self._render(LOGIN)
                return
            self.state.current_user = await self.state.auth_service.get_current_user()
            if not self.state.is_authenticated:
                self.state.clear_session()
                self._render(LOGIN)
                return
            if await self._load_workspace(self.enter_demo):
                log.info("Entered mock-authenticated workspace as %s", user.role)
                self._render(HOME)
        except Exception as exc:
            log.exception("Mock sign-in failed")
            self._show_error(exc, self.enter_demo)

    async def sign_out(self) -> None:
        try:
            await self.state.auth_service.logout()
        except Exception:
            log.exception("Authentication provider sign-out failed")
        finally:
            self.state.clear_session()
            self._render(LOGIN)

    def go(self, path: str) -> None:
        valid_routes = (
            LOGIN, HOME, REPORTS, JOB_CARDS, NOTIFICATIONS, PROFILE,
            CREATE_REPORT_ROUTE, REPORT_DETAIL, JOB_CARD_DETAIL,
        )
        if path not in valid_routes:
            log.warning("Unknown route requested: %s", path)
            path = LOGIN
        if path != LOGIN and not self.state.is_authenticated:
            path = LOGIN
        elif path != LOGIN and not can_access_route(self.state.current_user, path, self.state.permission_service):
            log.info("Role %s cannot access %s; returning to Home", self.state.current_user.role, path)
            path = HOME
        self._render(path)

    async def _load_workspace(self, retry) -> bool:
        self.page.clean()
        self.page.add(loading_indicator("Loading your workspace…"))
        self.page.update()
        try:
            dashboard, reports, job_cards, notifications = await asyncio.gather(
                self.state.service.get_dashboard_summary(),
                self.state.report_service.get_reports(),
                self.state.job_card_service.get_job_cards(),
                self.state.service.get_notifications(),
            )
            lockout_records = await asyncio.gather(*(
                self.state.lockout_service.get_for_job_card(card.job_card_id)
                for card in job_cards
            ))
            positive_test_records = await asyncio.gather(*(
                self.state.positive_test_service.get_for_job_card(card.job_card_id)
                for card in job_cards
            ))
        except Exception as exc:
            log.exception("Could not load BDR workspace")
            self._show_error(exc, retry)
            return False
        self.state.dashboard = dashboard
        self.state.reports = reports
        self.state.job_cards = job_cards
        self.state.lockouts = {
            record.job_card_id: record for record in lockout_records if record is not None
        }
        self.state.positive_tests = {
            card.job_card_id: records
            for card, records in zip(job_cards, positive_test_records)
        }
        self.state.notifications = notifications
        return True

    def _show_error(self, error: Exception, retry) -> None:
        self.page.clean()
        self.page.add(
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[error_state(str(error), retry)],
            )
        )
        self.page.update()

    def _render(self, path: str) -> None:
        self.state.current_route = path
        self.page.clean()
        builders = {
            LOGIN: build_login_screen,
            HOME: build_home_screen,
            REPORTS: build_reports_screen,
            REPORT_DETAIL: build_report_detail_screen,
            JOB_CARDS: build_job_cards_screen,
            JOB_CARD_DETAIL: build_job_card_detail_screen,
            NOTIFICATIONS: build_notifications_screen,
            PROFILE: build_profile_screen,
            CREATE_REPORT_ROUTE: build_create_report_screen,
        }
        self.page.add(builders[path](self.page, self.state, self))
        self.page.update()
