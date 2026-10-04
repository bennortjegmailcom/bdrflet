"""Job card list and status overview."""

import flet as ft

from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.feedback_states import empty_state
from app.components.status_badge import status_badge
from app.routes import JOB_CARD_DETAIL, JOB_CARDS
from app.state import AppState
from app.theme import MUTED, NAVY


_TERMINAL_STATUSES = {"WORK_COMPLETE", "RESOLVED"}


def build_job_cards_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    def make_open_card(job_card_id: str):
        def open_card() -> None:
            state.selected_job_card_id = job_card_id
            router.go(JOB_CARD_DETAIL)

        return open_card

    cards: list[ft.Control] = []
    for item in state.job_cards:
        cards.append(
            ft.Container(
                ink=True,
                on_click=make_open_card(item.job_card_id),
                padding=16,
                border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                border_radius=14,
                bgcolor=ft.Colors.WHITE,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[ft.Text(item.job_card_id, size=12, color=MUTED), status_badge(item.status)],
                        ),
                        ft.Text(item.equipment, size=15, weight=ft.FontWeight.W_600, color=NAVY),
                        ft.Text(item.problem_description, size=13, color=NAVY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"Report · {item.report_id} · {item.equipment_id}", size=12, color=MUTED),
                        ft.Text(f"Assigned · {item.assigned_worker} · {item.workgroup}", size=12, color=MUTED),
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text("Lockout", size=12, color=MUTED),
                                status_badge(item.lockout_status.replace("_", " ")),
                            ],
                        ),
                        ft.Text(f"Updated · {item.updated_at}", size=11, color=ft.Colors.BLUE_GREY_400),
                    ],
                ),
            )
        )
    if not cards:
        cards = [empty_state("No job cards", "Assigned maintenance work will show here.", icon=ft.Icons.ASSIGNMENT)]

    open_count = sum(1 for item in state.job_cards if item.status not in _TERMINAL_STATUSES)
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=14,
                    controls=[
                        app_header("Job Cards", "Work linked to breakdown reports."),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20),
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text("Open work", size=14, weight=ft.FontWeight.W_600, color=NAVY),
                                    status_badge(str(open_count), "pending"),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20, vertical=4),
                            content=ft.Column(tight=True, spacing=12, controls=cards),
                        ),
                    ],
                ),
                bottom_navigation(JOB_CARDS, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
