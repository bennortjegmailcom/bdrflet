"""Dialogs used by the controlled lockout workflow."""

import flet as ft

from app.models.job_card import JobCard
from app.models.lockout import Lockout
from app.state import AppState
from app.theme import MUTED, NAVY


def info_line(label: str, value: str) -> ft.Control:
    return ft.Row(
        spacing=6,
        controls=[
            ft.Text(f"{label}:", size=12, weight=ft.FontWeight.W_600, color=NAVY),
            ft.Text(value or "—", size=12, color=NAVY, selectable=True),
        ],
    )


def show_reason_dialog(page: ft.Page, title: str, submit, refresh, *, initial_reason: str = "") -> None:
    reason = ft.TextField(
        label="Reason (required)",
        value=initial_reason,
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    error = ft.Text("", size=12, color=ft.Colors.RED_700)

    async def save_rejection() -> None:
        if not (reason.value or "").strip():
            reason.error = "A reason is required."
            page.update()
            return
        try:
            result: Lockout = await submit((reason.value or "").strip())
        except (ValueError, PermissionError) as exc:
            error.value = str(exc)
            page.update()
            return
        except Exception:
            error.value = "Could not record the rejection. Please try again."
            page.update()
            return
        page.pop_dialog()
        await refresh(result)

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=NAVY, weight=ft.FontWeight.BOLD),
            content=ft.Column(tight=True, controls=[reason, error]),
            actions=[
                ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                ft.Button(content="Submit rejection", on_click=save_rejection),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    )


def show_equipment_scan_dialog(
    page: ft.Page,
    state: AppState,
    job: JobCard,
    on_match,
    on_mismatch,
) -> None:
    qr_field = ft.TextField(
        label="Equipment QR code",
        hint_text="Scan or enter the QR payload",
        autofocus=True,
    )
    result_text = ft.Text("", size=12, color=MUTED)

    async def scan_equipment() -> None:
        result = await state.equipment_identification_service.scan_and_resolve(
            qr_field.value, job.equipment_id
        )
        if result.unknown:
            result_text.value = "Unknown equipment QR. Lockout cannot continue."
            page.update()
            return
        if result.equipment is None:
            result_text.value = "Enter or scan an equipment QR code to continue."
            page.update()
            return
        if result.mismatch:
            page.pop_dialog()
            on_mismatch(result.equipment.equipment_id)
            page.update()
            return
        on_match(result.equipment)
        page.pop_dialog()
        page.update()

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text("Scan equipment", color=NAVY, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                tight=True,
                spacing=8,
                controls=[
                    info_line("Job card equipment ID", job.equipment_id),
                    qr_field,
                    result_text,
                    ft.Text(
                        "Preview mode uses the QR scanner adapter with a typed QR payload.",
                        size=12,
                        color=MUTED,
                    ),
                ],
            ),
            actions=[
                ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                ft.Button(content="Resolve QR", on_click=scan_equipment),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    )
