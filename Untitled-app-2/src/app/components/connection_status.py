import flet as ft

from app.components.status_badge import status_badge


def connection_status() -> ft.Control:
    return status_badge("DEMO · OFFLINE", "offline")
