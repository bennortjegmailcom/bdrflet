import flet as ft

from app.components.branding import brand_lockup
from app.components.status_badge import status_badge
from app.theme import MUTED, NAVY


def app_header(
    title: str,
    subtitle: str = "",
    *,
    show_brand: bool = False,
    connection_status: str = "ONLINE",
) -> ft.Control:
    leading = brand_lockup(compact=True) if show_brand else ft.Text(
        title,
        size=24,
        weight=ft.FontWeight.BOLD,
        color=NAVY,
        expand=True,
    )
    controls: list[ft.Control] = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[leading, status_badge(connection_status, connection_status)],
        )
    ]
    if show_brand:
        controls.append(ft.Text(title, size=25, weight=ft.FontWeight.BOLD, color=NAVY))
    if subtitle:
        controls.append(ft.Text(subtitle, size=14, color=MUTED))
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=18, bottom=4),
        content=ft.Column(tight=True, spacing=6, controls=controls),
    )
