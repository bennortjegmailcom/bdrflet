import flet as ft

from app.components.branding import brand_lockup
from app.components.connection_status import connection_status
from app.state import AppState
from app.theme import MUTED, NAVY, TEAL


def build_login_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    return ft.SafeArea(
        expand=True,
        content=ft.Container(
            expand=True,
            padding=24,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=0,
                controls=[
                    brand_lockup(),
                    ft.Container(height=30),
                    ft.Row(tight=True, controls=[connection_status()]),
                    ft.Container(height=24),
                    ft.Text("Your shift, in view.", size=29, weight=ft.FontWeight.BOLD, color=NAVY),
                    ft.Container(height=9),
                    ft.Text(
                        "A mobile companion for staying up to date on breakdown reports and maintenance activity.",
                        size=15,
                        color=MUTED,
                    ),
                    ft.Container(height=25),
                    ft.Container(
                        padding=20,
                        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                        border_radius=16,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Column(
                            tight=True,
                            spacing=12,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(ft.Icons.INFO_OUTLINE, color=TEAL, size=20),
                                        ft.Text("Backend connection pending", size=15, weight=ft.FontWeight.W_600, color=NAVY),
                                    ],
                                ),
                                ft.Text(
                                    "Production sign-in will be enabled when the BDR service is connected. Explore the interface in demo mode for now.",
                                    size=13,
                                    color=MUTED,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(height=20),
                    ft.Button(
                        content="Continue in demo mode",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=router.enter_demo,
                        bgcolor=TEAL,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Container(height=14),
                    ft.Text(
                        "Demo workspace · No credentials required",
                        size=12,
                        color=MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        ),
    )
