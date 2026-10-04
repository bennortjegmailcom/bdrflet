import flet as ft

from app.components.app_header import app_header
from app.components.bottom_navigation import bottom_navigation
from app.components.confirmation_dialog import show_confirmation
from app.routes import PROFILE
from app.state import AppState
from app.theme import MUTED, NAVY, TEAL


def _detail_row(icon: str, label: str, value: str) -> ft.Control:
    return ft.Row(
        spacing=14,
        controls=[
            ft.Icon(icon, size=20, color=TEAL),
            ft.Column(
                tight=True,
                spacing=3,
                controls=[
                    ft.Text(label, size=11, color=MUTED),
                    ft.Text(value, size=14, color=NAVY, weight=ft.FontWeight.W_500),
                ],
            ),
        ],
    )


def build_profile_screen(page: ft.Page, state: AppState, router) -> ft.Control:
    def confirm_sign_out() -> None:
        show_confirmation(
            page,
            title="Log out?",
            message="Are you sure you want to leave this demo workspace?",
            on_confirm=router.sign_out,
            confirm_label="Log out",
        )

    profile = state.profile
    name = profile.name if profile else "Demo user"
    role = profile.role if profile else ""
    site = profile.workgroup if profile else ""
    email = profile.email if profile else ""

    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=20,
                    controls=[
                        app_header("Profile", "Your account and site details."),
                        ft.Container(
                            margin=ft.Margin.symmetric(horizontal=20),
                            padding=22,
                            border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                            border_radius=16,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                tight=True,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=72,
                                        height=72,
                                        alignment=ft.Alignment.CENTER,
                                        border_radius=36,
                                        bgcolor=ft.Colors.TEAL_50,
                                        content=ft.Icon(ft.Icons.PERSON, color=TEAL, size=36),
                                    ),
                                    ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=NAVY),
                                    ft.Text(role, size=13, color=MUTED),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                                        border_radius=16,
                                        bgcolor=ft.Colors.AMBER_50,
                                        content=ft.Text("DEMO ACCOUNT", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            margin=ft.Margin.symmetric(horizontal=20),
                            padding=20,
                            border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                            border_radius=16,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                tight=True,
                                spacing=19,
                                controls=[
                                    ft.Text("Account details", size=16, weight=ft.FontWeight.BOLD, color=NAVY),
                                    _detail_row(ft.Icons.EMAIL_OUTLINED, "Email", email),
                                    ft.Divider(color=ft.Colors.BLUE_GREY_100, thickness=1),
                                    _detail_row(ft.Icons.FACTORY, "Workgroup", site),
                                    ft.Divider(color=ft.Colors.BLUE_GREY_100, thickness=1),
                                    _detail_row(ft.Icons.WORK_OUTLINE, "Role", role),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=20),
                            content=ft.Button(
                                content="Log out",
                                icon=ft.Icons.LOGOUT,
                                on_click=confirm_sign_out,
                                bgcolor=ft.Colors.WHITE,
                                color=ft.Colors.RED_700,
                            ),
                        ),
                    ],
                ),
                bottom_navigation(PROFILE, router.go, state.current_user, state.permission_service),
            ],
        ),
    )
