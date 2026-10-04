import flet as ft

from app.permissions import allowed_routes_for
from app.routes import HOME, JOB_CARDS, NOTIFICATIONS, PROFILE, REPORTS
from app.theme import MUTED, NAVY, TEAL


_ITEMS = (
    ("Home", ft.Icons.HOME, HOME),
    ("Reports", ft.Icons.DESCRIPTION, REPORTS),
    ("Job Cards", ft.Icons.ASSIGNMENT, JOB_CARDS),
    ("Notifications", ft.Icons.NOTIFICATIONS_NONE, NOTIFICATIONS),
    ("Profile", ft.Icons.PERSON, PROFILE),
)


def bottom_navigation(active_route: str, on_navigate, user, permission_service) -> ft.Control:
    allowed_routes = allowed_routes_for(user, permission_service)

    def item(label: str, icon: str, route: str) -> ft.Control:
        active = active_route == route
        return ft.Container(
            expand=True,
            ink=True,
            on_click=lambda: on_navigate(route),
            padding=ft.Padding.symmetric(vertical=9),
            content=ft.Column(
                tight=True,
                spacing=3,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=20, color=TEAL if active else MUTED),
                    ft.Text(
                        label,
                        size=9,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                        color=NAVY if active else MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    visible_items = [item(label, icon, route) for label, icon, route in _ITEMS if route in allowed_routes]
    return ft.Container(
        border=ft.Border(top=ft.BorderSide(1, ft.Colors.BLUE_GREY_100)),
        bgcolor=ft.Colors.WHITE,
        content=ft.Row(spacing=0, controls=visible_items),
    )
