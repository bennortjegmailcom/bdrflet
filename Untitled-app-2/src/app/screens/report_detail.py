"""Authorized breakdown report detail and timeline view."""

import flet as ft

from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.feedback_states import empty_state
from app.components.status_badge import status_badge
from app.routes import REPORTS
from app.state import AppState
from app.theme import MUTED, NAVY


def _detail_line(label: str, value: str) -> ft.Control:
    return ft.Column(
        tight=True,
        spacing=3,
        controls=[
            ft.Text(label, size=11, color=MUTED),
            ft.Text(value or "—", size=14, color=NAVY),
        ],
    )


def _attachment_list(title: str, files, icon: str, *, image_previews: bool = False) -> ft.Control:
    controls: list[ft.Control] = [ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=NAVY)]
    if files:
        for file in files:
            if image_previews and file.content:
                controls.append(
                    ft.Container(
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Column(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.Image(src=file.content, width=180, height=120, fit=ft.BoxFit.COVER),
                                ft.Text(file.filename, size=12, color=NAVY),
                            ],
                        ),
                    )
                )
            else:
                controls.append(
                    ft.Container(
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                        border_radius=10,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(icon, color=ft.Colors.TEAL_700),
                                ft.Text(file.filename, size=13, color=NAVY, expand=True),
                            ],
                        ),
                    )
                )
    else:
        controls.append(ft.Text("No files attached", size=13, color=MUTED))
    return ft.Column(tight=True, spacing=8, controls=controls)


def build_report_detail_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    report = next((item for item in state.reports if item.reference == state.selected_report_id), None)
    if report is None:
        content = empty_state("Report unavailable", "This report is no longer in your authorized report list.")
    else:
        timeline = report.history or ()
        known_attachments = set((*report.photos, *report.audio_attachments))
        other_attachments = tuple(
            attachment for attachment in report.attachments
            if attachment not in known_attachments
        )
        timeline_controls = [
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.TEAL_600),
                    ft.Column(
                        expand=True,
                        tight=True,
                        spacing=3,
                        controls=[
                            ft.Text(entry.message, size=13, color=NAVY),
                            ft.Text(f"{entry.timestamp} · {entry.actor}", size=11, color=MUTED),
                        ],
                    ),
                ],
            )
            for entry in timeline
        ] or [ft.Text("No report history recorded.", size=13, color=MUTED)]
        content = ft.Column(
            tight=True,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[ft.Text(report.reference, size=15, weight=ft.FontWeight.BOLD, color=NAVY), status_badge(report.status)],
                ),
                ft.Text(report.problem_description, size=20, weight=ft.FontWeight.BOLD, color=NAVY),
                ft.Row(
                    spacing=8,
                    controls=[ft.Text("Priority", size=12, color=MUTED), status_badge(report.priority)],
                ),
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                _detail_line("Equipment", report.equipment or report.asset),
                _detail_line("Equipment ID", report.equipment_id),
                _detail_line("Area", report.area),
                _detail_line("Date / time", report.created_at or report.age),
                _detail_line("Location", report.location),
                _detail_line("Assigned workgroup", report.assigned_workgroup or report.workgroup),
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                _attachment_list("Photos", report.photos, ft.Icons.IMAGE, image_previews=True),
                _attachment_list("Audio", report.audio_attachments, ft.Icons.AUDIO_FILE),
                _attachment_list("Other attachments", other_attachments, ft.Icons.ATTACH_FILE),
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                ft.Text("History", size=16, weight=ft.FontWeight.W_600, color=NAVY),
                *timeline_controls,
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
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda: router.go(REPORTS)),
                        ft.Container(expand=True, content=app_header("Report details", "Breakdown report record.")),
                    ],
                ),
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[ft.Container(padding=ft.Padding.symmetric(horizontal=20, vertical=10), content=content)],
                ),
                bottom_navigation(REPORTS, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
