import flet as ft

from app.components.status_badge import status_badge
from app.theme import MUTED, NAVY


def work_item_card(
    *,
    title: str,
    subtitle: str,
    reference: str,
    time_label: str,
    status: str,
    icon: str,
) -> ft.Control:
    return ft.Container(
        padding=16,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=14,
        bgcolor=ft.Colors.WHITE,
        content=ft.Row(
            spacing=13,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    content=ft.Icon(icon, size=21, color=ft.Colors.TEAL_700),
                ),
                ft.Column(
                    expand=True,
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(reference, size=11, color=MUTED),
                                status_badge(status),
                            ],
                        ),
                        ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=NAVY),
                        ft.Text(subtitle, size=12, color=MUTED),
                        ft.Text(time_label, size=11, color=ft.Colors.BLUE_GREY_400),
                    ],
                ),
            ],
        ),
    )
