import flet as ft


def status_badge(label: str, tone: str | None = None) -> ft.Control:
    normalized = (tone or label).strip().lower()
    palette = {
        "new": (ft.Colors.AMBER_50, ft.Colors.AMBER_900),
        "pending": (ft.Colors.AMBER_50, ft.Colors.AMBER_900),
        "in review": (ft.Colors.TEAL_50, ft.Colors.TEAL_900),
        "in progress": (ft.Colors.TEAL_50, ft.Colors.TEAL_900),
        "assigned": (ft.Colors.BLUE_50, ft.Colors.BLUE_900),
        "scheduled": (ft.Colors.BLUE_GREY_50, ft.Colors.BLUE_GREY_800),
        "success": (ft.Colors.GREEN_50, ft.Colors.GREEN_900),
        "error": (ft.Colors.RED_50, ft.Colors.RED_900),
        "demo": (ft.Colors.AMBER_50, ft.Colors.BLUE_GREY_800),
        "offline": (ft.Colors.AMBER_50, ft.Colors.BLUE_GREY_800),
        "online": (ft.Colors.GREEN_50, ft.Colors.GREEN_900),
        "syncing": (ft.Colors.BLUE_50, ft.Colors.BLUE_900),
        "sync error": (ft.Colors.RED_50, ft.Colors.RED_900),
    }
    background, foreground = palette.get(
        normalized,
        (ft.Colors.BLUE_GREY_50, ft.Colors.BLUE_GREY_800),
    )
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=16,
        bgcolor=background,
        content=ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color=foreground),
    )
