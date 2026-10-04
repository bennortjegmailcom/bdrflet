import flet as ft

from app.components.action_buttons import secondary_button
from app.theme import MUTED, NAVY, TEAL


def loading_indicator(message: str = "Loading…") -> ft.Control:
    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        controls=[
            ft.ProgressRing(width=34, height=34, stroke_width=3, color=TEAL),
            ft.Text(message, size=14, color=MUTED),
        ],
    )


def empty_state(
    title: str,
    message: str,
    *,
    icon: str = ft.Icons.INBOX_OUTLINED,
    action: ft.Control | None = None,
) -> ft.Control:
    controls: list[ft.Control] = [
        ft.Icon(icon, size=38, color=ft.Colors.BLUE_GREY_300),
        ft.Text(title, size=17, weight=ft.FontWeight.W_600, color=NAVY, text_align=ft.TextAlign.CENTER),
        ft.Text(message, size=13, color=MUTED, text_align=ft.TextAlign.CENTER),
    ]
    if action is not None:
        controls.append(action)
    return ft.Column(
        tight=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=controls,
    )


def error_state(message: str, on_retry) -> ft.Control:
    return ft.Column(
        tight=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=38, color=ft.Colors.RED_600),
            ft.Text("Something went wrong", size=17, weight=ft.FontWeight.W_600, color=NAVY),
            ft.Text(message, size=13, color=MUTED, text_align=ft.TextAlign.CENTER),
            secondary_button("Try again", on_retry, icon=ft.Icons.REFRESH),
        ],
    )
