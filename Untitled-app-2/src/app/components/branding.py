import flet as ft

from app.theme import NAVY, TEAL


def brand_lockup(compact: bool = False) -> ft.Control:
    mark = ft.Container(
        width=48 if not compact else 42,
        height=48 if not compact else 42,
        alignment=ft.Alignment.CENTER,
        border_radius=13,
        bgcolor=TEAL,
        content=ft.Icon(
            ft.Icons.PRECISION_MANUFACTURING,
            color=ft.Colors.WHITE,
            size=26 if not compact else 22,
        ),
    )
    title = ft.Column(
        tight=True,
        spacing=2,
        controls=[
            ft.Text("BDR", size=20 if compact else 24, weight=ft.FontWeight.BOLD, color=NAVY),
            ft.Text(
                "MOBILE COMPANION" if not compact else "BREAKDOWN REPORTER",
                size=10,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.BLUE_GREY_600,
            ),
        ],
    )
    return ft.Row(tight=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[mark, title])
