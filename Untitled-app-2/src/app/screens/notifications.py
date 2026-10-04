import flet as ft

from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.feedback_states import empty_state
from app.components.status_badge import status_badge
from app.routes import NOTIFICATIONS
from app.state import AppState
from app.theme import MUTED, NAVY


def _notification_card(item) -> ft.Control:
    return ft.Container(
        padding=16,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=14,
        bgcolor=ft.Colors.WHITE,
        content=ft.Row(
            spacing=13,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(
                    ft.Icons.NOTIFICATIONS_ACTIVE if item.unread else ft.Icons.NOTIFICATIONS_NONE,
                    color=ft.Colors.TEAL_700 if item.unread else ft.Colors.BLUE_GREY_400,
                    size=22,
                ),
                ft.Column(
                    expand=True,
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(item.title, size=14, weight=ft.FontWeight.W_600, color=NAVY, expand=True),
                                status_badge("New", "new") if item.unread else ft.Container(width=1),
                            ],
                        ),
                        ft.Text(item.message, size=12, color=MUTED),
                        ft.Text(item.age, size=11, color=ft.Colors.BLUE_GREY_400),
                    ],
                ),
            ],
        ),
    )


def build_notifications_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    cards = [_notification_card(item) for item in state.notifications]
    if not cards:
        cards = [empty_state("You're all caught up", "New BDR updates will appear here.", icon=ft.Icons.NOTIFICATIONS_NONE)]

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=16,
                    controls=[
                        app_header("Notifications", "Updates about reports and assigned work."),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20, vertical=4),
                            content=ft.Column(tight=True, spacing=12, controls=cards),
                        ),
                    ],
                ),
                bottom_navigation(NOTIFICATIONS, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
