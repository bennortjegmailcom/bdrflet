"""Job card detail, photos, work notes, and controlled lockout workflow."""

import flet as ft

from app.components.action_buttons import primary_button
from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.feedback_states import empty_state
from app.components.lockout_workflow import build_lockout_workflow
from app.components.positive_test_workflow import build_positive_test_workflow
from app.components.status_badge import status_badge
from app.routes import JOB_CARDS, REPORT_DETAIL
from app.services.permission_service import UPDATE_JOB_CARD, VIEW_REPORT
from app.state import AppState
from app.theme import MUTED, NAVY


def _detail_line(label: str, value: str) -> ft.Control:
    return ft.Column(
        tight=True,
        spacing=3,
        controls=[ft.Text(label, size=11, color=MUTED), ft.Text(value or "—", size=14, color=NAVY)],
    )


def _photo_item(item) -> ft.Control:
    if item.content:
        return ft.Container(
            padding=10,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            content=ft.Column(
                tight=True,
                spacing=6,
                controls=[
                    ft.Image(src=item.content, width=180, height=120, fit=ft.BoxFit.COVER),
                    ft.Text(item.filename, size=12, color=NAVY),
                ],
            ),
        )
    return ft.Container(
        padding=10,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        content=ft.Row(
            spacing=10,
            controls=[ft.Icon(ft.Icons.IMAGE, color=ft.Colors.TEAL_700), ft.Text(item.filename, size=13, color=NAVY)],
        ),
    )


def build_job_card_detail_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    job = next((item for item in state.job_cards if item.job_card_id == state.selected_job_card_id), None)
    if job is None:
        detail_content = empty_state("Job card unavailable", "This job card is no longer in your authorized list.")
    else:
        notes_column = ft.Column(
            tight=True,
            spacing=8,
            controls=[ft.Text(note, size=13, color=NAVY) for note in job.notes]
            or [ft.Text("No work notes yet.", size=13, color=MUTED)],
        )
        note_field = ft.TextField(
            label="Add work note",
            hint_text="Record work performed or findings",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        note_error = ft.Text("", size=12, color=ft.Colors.RED_700)

        async def add_note() -> None:
            try:
                updated = await state.job_card_service.add_work_note(job.job_card_id, note_field.value or "")
            except ValueError as exc:
                note_error.value = str(exc)
                page.update()
                return
            except Exception:
                note_error.value = "Could not save the work note. Please try again."
                page.update()
                return
            if updated is None:
                note_error.value = "Job card is no longer available."
                page.update()
                return
            state.job_cards = tuple(
                updated if item.job_card_id == updated.job_card_id else item
                for item in state.job_cards
            )
            note_field.value = ""
            note_error.value = ""
            notes_column.controls = [ft.Text(note, size=13, color=NAVY) for note in updated.notes]
            page.update()

        photos = [_photo_item(item) for item in job.photos] or [
            ft.Text("No photos attached.", size=13, color=MUTED)
        ]
        controls: list[ft.Control] = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(job.job_card_id, size=15, weight=ft.FontWeight.BOLD, color=NAVY), status_badge(job.status)],
            ),
            ft.Text(job.problem_description, size=20, weight=ft.FontWeight.BOLD, color=NAVY),
            _detail_line("Linked breakdown report", job.report_id),
            _detail_line("Equipment", job.equipment),
            _detail_line("Equipment ID", job.equipment_id),
            _detail_line("Area", job.area),
            _detail_line("Priority", job.priority),
            _detail_line("Workgroup", job.workgroup),
            _detail_line("Assigned worker", job.assigned_worker),
            _detail_line("Created", job.created_at),
            _detail_line("Last updated", job.updated_at),
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Text("Photos", size=16, weight=ft.FontWeight.W_600, color=NAVY),
            *photos,
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Text("Work notes", size=16, weight=ft.FontWeight.W_600, color=NAVY),
            notes_column,
        ]
        if state.permission_service.has_permission(state.current_user, UPDATE_JOB_CARD):
            controls.extend([note_field, note_error, primary_button("Save work note", add_note)])
        controls.extend([
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            build_lockout_workflow(page, state, job, router),
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            build_positive_test_workflow(page, state, job, router),
        ])
        if state.permission_service.has_permission(state.current_user, VIEW_REPORT):
            def open_report() -> None:
                state.selected_report_id = job.report_id
                router.go(REPORT_DETAIL)

            controls.extend([ft.Divider(color=ft.Colors.BLUE_GREY_100), primary_button("Open linked report", open_report)])
        detail_content = ft.Column(tight=True, spacing=14, controls=controls)

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda: router.go(JOB_CARDS)),
                        ft.Container(expand=True, content=app_header("Job card details", "Maintenance work record.", connection_status=state.connectivity_service.status.value)),
                    ],
                ),
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[ft.Container(padding=ft.Padding.symmetric(horizontal=20, vertical=10), content=detail_content)],
                ),
                bottom_navigation(JOB_CARDS, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
