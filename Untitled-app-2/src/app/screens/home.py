import flet as ft

from app.components.action_buttons import primary_button, secondary_button
from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.work_item_card import work_item_card
from app.permissions import can_access_route
from app.services.permission_service import CREATE_REPORT, UPDATE_JOB_CARD
from app.routes import CREATE_REPORT_ROUTE, HOME, JOB_CARDS, NOTIFICATIONS, REPORTS
from app.state import AppState
from app.theme import AMBER, MUTED, NAVY, TEAL


def _summary_card(label: str, value: int, icon: str, accent: str) -> ft.Control:
    return ft.Container(
        padding=18,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=15,
        bgcolor=ft.Colors.WHITE,
        content=ft.Row(
            spacing=14,
            controls=[
                ft.Container(
                    width=44,
                    height=44,
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    content=ft.Icon(icon, color=accent, size=23),
                ),
                ft.Column(
                    tight=True,
                    spacing=2,
                    controls=[
                        ft.Text(label, size=13, color=MUTED),
                        ft.Text(str(value), size=23, weight=ft.FontWeight.BOLD, color=NAVY),
                    ],
                ),
            ],
        ),
    )


def build_home_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    dashboard = state.dashboard
    summary_cards: list[ft.Control] = []
    recent_items: list[ft.Control] = []
    if dashboard:
        summary_cards = [
            _summary_card("Open breakdown reports", dashboard.open_reports, ft.Icons.WARNING_AMBER, AMBER),
            _summary_card("Awaiting review", dashboard.awaiting_review, ft.Icons.RATE_REVIEW, TEAL),
            _summary_card("Resolved this week", dashboard.resolved_this_week, ft.Icons.TASK_ALT, ft.Colors.GREEN_600),
        ]
        recent_items = [
            work_item_card(
                title=item.title,
                subtitle=item.asset,
                reference="Recent activity",
                time_label=item.age,
                status=item.status,
                icon=ft.Icons.BUILD,
            )
            for item in dashboard.recent_activity
        ]

    quick_actions: list[ft.Control] = []
    if state.permission_service.has_permission(state.current_user, CREATE_REPORT):
        quick_actions.append(
            ft.Row(controls=[primary_button("New Breakdown Report", lambda: router.go(CREATE_REPORT_ROUTE), icon=ft.Icons.ADD_CIRCLE_OUTLINE, expand=True)])
        )
    if can_access_route(state.current_user, REPORTS, state.permission_service):
        quick_actions.append(
            ft.Row(controls=[secondary_button("My Reports", lambda: router.go(REPORTS), icon=ft.Icons.DESCRIPTION, expand=True)])
        )
    if can_access_route(state.current_user, JOB_CARDS, state.permission_service):
        quick_actions.append(
            ft.Row(controls=[secondary_button("My Job Cards", lambda: router.go(JOB_CARDS), icon=ft.Icons.ASSIGNMENT, expand=True)])
        )
    if state.permission_service.has_permission(state.current_user, UPDATE_JOB_CARD):
        quick_actions.append(
            ft.Row(controls=[secondary_button("Pending Actions", lambda: router.go(JOB_CARDS), icon=ft.Icons.PENDING_ACTIONS, expand=True)])
        )
    if can_access_route(state.current_user, NOTIFICATIONS, state.permission_service):
        quick_actions.append(
            ft.Row(controls=[secondary_button("Notifications", lambda: router.go(NOTIFICATIONS), icon=ft.Icons.NOTIFICATIONS_NONE, expand=True)])
        )

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=18,
                    controls=[
                        app_header(
                            f"Good day, {state.profile.name.split()[0] if state.profile else 'there'}",
                            "Here’s the latest from your site.",
                            show_brand=True,
                            connection_status=state.connectivity_service.status.value,
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20),
                            content=ft.Column(
                                tight=True,
                                spacing=10,
                                controls=[
                                    ft.Text("Quick actions", size=17, weight=ft.FontWeight.BOLD, color=NAVY),
                                    *quick_actions,
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20),
                            content=ft.Column(
                                tight=True,
                                spacing=12,
                                controls=[
                                    ft.Text("Breakdown overview", size=17, weight=ft.FontWeight.BOLD, color=NAVY),
                                    *summary_cards,
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=ft.Padding.only(left=20, right=20, bottom=18),
                            content=ft.Column(
                                tight=True,
                                spacing=12,
                                controls=[
                                    ft.Text("Recent activity", size=17, weight=ft.FontWeight.BOLD, color=NAVY),
                                    *recent_items,
                                ],
                            ),
                        ),
                    ],
                ),
                bottom_navigation(HOME, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
