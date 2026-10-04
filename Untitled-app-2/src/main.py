import logging

import flet as ft

from app.routes import AppRouter
from app.services.auth_service import MockAuthService
from app.services.bdr_service import DemoBdrService
from app.services.demo_repository import MockBdrRepository
from app.services.equipment_identification_service import EquipmentIdentificationService
from app.services.equipment_service import EquipmentService
from app.services.job_card_service import JobCardService
from app.services.lockout_service import LockoutService
from app.services.positive_test_service import PositiveTestService
from app.services.permission_service import PermissionService
from app.services.qr_scanner import MockQRScanner
from app.services.report_service import ReportService
from app.state import AppState
from app.theme import APP_THEME

LOG_LEVEL = logging.INFO
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("app").setLevel(LOG_LEVEL)
log = logging.getLogger("app.main")


async def main(page: ft.Page) -> None:
    page.title = "BDR Mobile"
    page.theme = APP_THEME
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0
    page.spacing = 0

    file_picker = ft.FilePicker()
    repository = MockBdrRepository()
    equipment_service = EquipmentService(repository)
    permission_service = PermissionService()
    lockout_service = LockoutService(repository, permission_service)
    state = AppState(
        service=DemoBdrService(),
        auth_service=MockAuthService(),
        report_service=ReportService(repository),
        job_card_service=JobCardService(repository),
        equipment_service=equipment_service,
        equipment_identification_service=EquipmentIdentificationService(
            MockQRScanner(), equipment_service
        ),
        lockout_service=lockout_service,
        positive_test_service=PositiveTestService(
            repository, lockout_service, permission_service
        ),
        permission_service=permission_service,
    )
    router = AppRouter(page, state, file_picker)
    log.info("Starting BDR Mobile")
    await router.initialize()


ft.run(main)
