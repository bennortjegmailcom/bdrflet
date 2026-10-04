"""Mobile workflow for composing and submitting a breakdown report."""

import logging

import flet as ft

from app.components.action_buttons import primary_button, secondary_button
from app.components.app_header import app_header
from app.components.equipment_selector import equipment_selector
from app.components.report_uploads import ReportUploadPicker
from app.models.equipment import Equipment
from app.models.report import BreakdownReportDraft
from app.routes import HOME, REPORTS
from app.services.permission_service import CREATE_REPORT
from app.state import AppState
from app.theme import NAVY, TEAL

log = logging.getLogger("app.create_report_screen")
_PRIORITY_OPTIONS = ("Low", "Normal", "High", "Urgent")


def build_create_report_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    """Build the report form; all report submission goes through ReportService."""
    user = state.current_user
    if not state.permission_service.has_permission(user, CREATE_REPORT):
        return ft.SafeArea(
            expand=True,
            content=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=36, color=ft.Colors.BLUE_GREY_400),
                    ft.Text("You don’t have permission to create reports.", color=NAVY),
                    secondary_button("Back to Home", lambda: router.go(HOME)),
                ],
            ),
        )

    equipment = ft.TextField(label="Equipment", hint_text="e.g. Transfer pump")
    equipment_id = ft.TextField(label="Equipment ID", hint_text="e.g. P-204")
    area = ft.TextField(label="Area", hint_text="e.g. Water treatment")
    problem = ft.TextField(
        label="Problem description",
        hint_text="Describe the fault and its impact",
        multiline=True,
        min_lines=3,
        max_lines=5,
    )
    priority = ft.Dropdown(
        label="Priority",
        hint_text="Select priority",
        options=[ft.DropdownOption(key=value, text=value) for value in _PRIORITY_OPTIONS],
    )
    workgroup = ft.TextField(label="Workgroup", value=user.workgroup if user else "")
    location = ft.TextField(label="Optional location", hint_text="e.g. Building 2, north side")
    uploads = ReportUploadPicker(page, router.file_picker)
    submission_error = ft.Text("", color=ft.Colors.RED_700, size=13)
    submit_button: ft.Control | None = None

    def apply_equipment(item: Equipment) -> None:
        equipment.value = item.description
        equipment_id.value = item.equipment_id
        area.value = item.area
        workgroup.value = item.workgroup
        page.update()

    lookup = equipment_selector(
        page,
        state.equipment_service,
        state.equipment_identification_service,
        equipment_id,
        apply_equipment,
    )

    def show_success(report_reference: str, job_reference: str) -> None:
        page.clean()
        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=58, color=TEAL),
                        ft.Text(
                            "Breakdown report submitted",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=NAVY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            padding=18,
                            border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                            border_radius=14,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                tight=True,
                                spacing=10,
                                controls=[
                                    ft.Text(f"Report reference: {report_reference}", color=NAVY),
                                    ft.Text(f"Job reference: {job_reference}", color=NAVY),
                                ],
                            ),
                        ),
                        ft.Row(
                            tight=True,
                            controls=[
                                primary_button("View My Reports", lambda: router.go(REPORTS)),
                                secondary_button("Home", lambda: router.go(HOME)),
                            ],
                        ),
                    ],
                ),
            )
        )
        page.update()

    async def submit_report() -> None:
        required_fields = (
            (equipment, "Equipment is required."),
            (equipment_id, "Equipment ID is required."),
            (area, "Area is required."),
            (problem, "Problem description is required."),
            (workgroup, "Workgroup is required."),
        )
        valid = True
        for field, error in required_fields:
            field.error = None if (field.value or "").strip() else error
            valid = valid and field.error is None
        priority.error_text = None if priority.value else "Priority is required."
        valid = valid and bool(priority.value)
        if not valid:
            page.update()
            return

        draft = BreakdownReportDraft(
            equipment=equipment.value.strip(),
            equipment_id=equipment_id.value.strip(),
            area=area.value.strip(),
            problem_description=problem.value.strip(),
            priority=priority.value,
            workgroup=workgroup.value.strip(),
            photo=uploads.photo,
            additional_photos=uploads.additional_photos,
            audio=uploads.audio,
            location=(location.value or "").strip() or None,
        )
        submission_error.value = ""
        if submit_button is not None:
            submit_button.disabled = True
            submit_button.content = "Submitting…"
        page.update()
        try:
            result = await state.report_service.submit_report(draft)
        except Exception:
            log.exception("Report submission failed")
            submission_error.value = "The report could not be submitted. Please try again."
            if submit_button is not None:
                submit_button.disabled = False
                submit_button.content = "Submit breakdown report"
            page.update()
            return

        try:
            state.reports = await state.report_service.get_reports()
            state.job_cards = await state.job_card_service.get_job_cards()
        except Exception:
            # The submission already succeeded; keep the confirmation visible if refresh fails.
            log.exception("Could not refresh report/job-card lists after submission")
        log.info("Report submitted with reference %s", result.report_reference)
        show_success(result.report_reference, result.job_reference)

    submit_button = primary_button("Submit breakdown report", submit_report, icon=ft.Icons.SEND, expand=True)
    form = ft.Column(
        tight=True,
        spacing=14,
        controls=[
            lookup,
            equipment,
            equipment_id,
            area,
            problem,
            priority,
            workgroup,
            uploads.control,
            location,
            submission_error,
            submit_button,
        ],
    )
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda: router.go(HOME)),
                        ft.Container(expand=True, content=app_header("New breakdown report", "Report an equipment issue.", connection_status=state.connectivity_service.status.value)),
                    ],
                ),
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[ft.Container(padding=ft.Padding.symmetric(horizontal=20, vertical=8), content=form)],
                ),
            ],
        ),
    )
