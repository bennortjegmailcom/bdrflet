import inspect

import flet as ft

from app.theme import NAVY


def show_confirmation(
    page: ft.Page,
    *,
    title: str,
    message: str,
    on_confirm,
    confirm_label: str = "Confirm",
) -> None:
    async def confirm() -> None:
        page.pop_dialog()
        result = on_confirm()
        if inspect.isawaitable(result):
            await result

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, color=NAVY, weight=ft.FontWeight.BOLD),
        content=ft.Text(message),
        actions=[
            ft.TextButton(content="Cancel", on_click=page.pop_dialog),
            ft.Button(content=confirm_label, on_click=confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialog)
