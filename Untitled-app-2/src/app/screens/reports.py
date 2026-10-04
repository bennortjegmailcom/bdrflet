"""Searchable and filterable mobile report list."""

import flet as ft

from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.feedback_states import empty_state
from app.components.status_badge import status_badge
from app.routes import REPORT_DETAIL, REPORTS
from app.state import AppState
from app.theme import MUTED, NAVY


def _report_card(report, on_open) -> ft.Control:
    equipment = report.equipment or report.asset
    description = report.problem_description or report.title
    workgroup = report.assigned_workgroup or report.workgroup or "Unassigned"
    timestamp = report.created_at or report.age
    return ft.Container(
        ink=True,
        on_click=on_open,
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
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(report.reference, size=12, color=MUTED),
                        status_badge(report.priority, "pending" if report.priority.casefold() in {"high", "urgent"} else "scheduled"),
                    ],
                ),
                ft.Text(equipment, size=15, weight=ft.FontWeight.W_600, color=NAVY),
                ft.Text(description, size=13, color=NAVY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[status_badge(report.status), ft.Text(timestamp, size=11, color=MUTED)],
                ),
                ft.Text(f"Workgroup · {workgroup}", size=12, color=MUTED),
            ],
        ),
    )


def build_reports_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    reports = state.reports
    search_field = ft.TextField(label="Search reports", hint_text="Report number, equipment, description…", prefix_icon=ft.Icons.SEARCH)
    status_options = ["All", *sorted({item.status for item in reports})]
    priority_options = ["All", *sorted({item.priority for item in reports})]
    status_filter = ft.Dropdown(
        label="Status",
        value="All",
        options=[ft.DropdownOption(key=value, text=value) for value in status_options],
    )
    priority_filter = ft.Dropdown(
        label="Priority",
        value="All",
        options=[ft.DropdownOption(key=value, text=value) for value in priority_options],
    )
    results = ft.Column(tight=True, spacing=12)
    result_count = ft.Text("", size=12, color=MUTED)

    def refresh_results(update_page: bool = True) -> None:
        query = (search_field.value or "").strip().casefold()
        status = status_filter.value or "All"
        priority = priority_filter.value or "All"
        filtered = [
            item for item in reports
            if (status == "All" or item.status == status)
            and (priority == "All" or item.priority == priority)
            and (
                not query
                or query in " ".join((
                    item.reference, item.equipment, item.equipment_id, item.asset,
                    item.title, item.priority, item.status, item.workgroup,
                    item.assigned_workgroup,
                )).casefold()
            )
        ]
        def make_open_report(report_id: str):
            def open_report() -> None:
                state.selected_report_id = report_id
                router.go(REPORT_DETAIL)

            return open_report

        cards: list[ft.Control] = [
            _report_card(report, make_open_report(report.reference))
            for report in filtered
        ]
        results.controls = cards or [empty_state("No matching reports", "Try changing the search or filters.")]
        result_count.value = f"{len(filtered)} report{'s' if len(filtered) != 1 else ''}"
        if update_page:
            page.update()

    def on_search_change() -> None:
        refresh_results()

    def on_status_select() -> None:
        refresh_results()

    def on_priority_select() -> None:
        refresh_results()

    search_field.on_change = on_search_change
    status_filter.on_select = on_status_select
    priority_filter.on_select = on_priority_select
    refresh_results(update_page=False)

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        app_header("My Reports", "Reports available to your account."),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20),
                            content=ft.Column(
                                tight=True,
                                spacing=10,
                                controls=[search_field, status_filter, priority_filter, result_count, results],
                            ),
                        ),
                        ft.Container(height=8),
                    ],
                ),
                bottom_navigation(REPORTS, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
