"""Audit event presentation for the lockout workflow panel."""

import flet as ft

from app.models.lockout import Lockout
from app.theme import MUTED, NAVY


def audit_history(record: Lockout | None) -> list[ft.Control]:
    if record is None or not record.audit_trail:
        return []
    controls: list[ft.Control] = [
        ft.Divider(color=ft.Colors.BLUE_GREY_100),
        ft.Text("AUDIT HISTORY", size=13, weight=ft.FontWeight.BOLD, color=NAVY),
    ]
    for event in reversed(record.audit_trail):
        controls.append(
            ft.Column(
                tight=True,
                spacing=3,
                controls=[
                    ft.Text(f"{event.action.replace('_', ' ')} · {event.timestamp}", size=12, weight=ft.FontWeight.W_600, color=NAVY),
                    ft.Text(f"User: {event.user_name} ({event.user_id})", size=11, color=MUTED),
                    ft.Text(f"Equipment {event.equipment_id} · Job {event.job_card_id} · Lockout {event.lockout_id}", size=11, color=MUTED),
                    ft.Text(f"{event.previous_state.value} → {event.new_state.value}", size=11, color=MUTED),
                    *([ft.Text(f"Reason: {event.reason}", size=11, color=MUTED)] if event.reason else []),
                ],
            )
        )
    return controls
