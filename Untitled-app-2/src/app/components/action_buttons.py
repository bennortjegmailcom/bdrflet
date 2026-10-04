import flet as ft

from app.theme import TEAL


def primary_button(label: str, on_click, *, icon: str | None = None, expand: bool = False) -> ft.Control:
    return ft.Button(
        content=label,
        icon=icon,
        on_click=on_click,
        bgcolor=TEAL,
        color=ft.Colors.WHITE,
        expand=expand,
    )


def secondary_button(label: str, on_click, *, icon: str | None = None, expand: bool = False) -> ft.Control:
    return ft.OutlinedButton(
        content=label,
        icon=icon,
        on_click=on_click,
        expand=expand,
    )
