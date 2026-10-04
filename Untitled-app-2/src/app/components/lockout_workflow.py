"""Lockout confirmation controls; all mutations are delegated to LockoutService."""

import flet as ft

from app.components.action_buttons import primary_button, secondary_button
from app.components.confirmation_dialog import show_confirmation
from app.components.lockout_audit_history import audit_history
from app.components.lockout_dialogs import (
    info_line,
    show_equipment_scan_dialog,
    show_reason_dialog,
)
from app.components.lockout_status import lockout_state_for, lockout_state_label
from app.models.equipment import Equipment
from app.models.job_card import JobCard
from app.models.lockout import Lockout, LockoutState
from app.services.permission_service import (
    APPROVE_LOCKOUT_RELEASE,
    CONFIRM_EQUIPMENT,
    CONFIRM_PHYSICAL_LOCKOUT,
    CONFIRM_SCADA_STOP,
    REQUEST_LOCKOUT,
    REQUEST_LOCKOUT_RELEASE,
)
from app.state import AppState
from app.theme import MUTED, NAVY


def build_lockout_workflow(page: ft.Page, state: AppState, job: JobCard, router) -> ft.Control:
    permissions = state.permission_service
    user = state.current_user
    record = state.lockouts.get(job.job_card_id)
    current = lockout_state_for(job, record)
    status_label = lockout_state_label(current)
    feedback = ft.Text("", size=12, color=ft.Colors.RED_700)
    scan_feedback = ft.Text("", size=12, color=MUTED)
    scanned_equipment_id: list[str | None] = [None]
    mismatch_blocked = [False]

    async def refresh(record_after: Lockout) -> None:
        state.lockouts[job.job_card_id] = record_after
        state.job_cards = await state.job_card_service.get_job_cards()
        router.go("/job-card-detail")

    async def request(reason: str) -> Lockout:
        return await state.lockout_service.request_lockout(job.job_card_id, user, reason)

    async def change(action: str, *args) -> None:
        methods = {
            "equipment": state.lockout_service.confirm_equipment,
            "scada": state.lockout_service.confirm_scada_stop,
            "physical": state.lockout_service.confirm_physical_lockout,
        }
        try:
            result = await methods[action](job.job_card_id, user, *args)
        except (ValueError, PermissionError) as exc:
            feedback.value = str(exc)
            page.update()
            return
        except Exception:
            feedback.value = "Could not update the lockout workflow. Please try again."
            page.update()
            return
        await refresh(result)

    def show_request_dialog() -> None:
        reason = ft.TextField(
            label="Reason for lockout request",
            hint_text="Describe why isolation is requested",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        error = ft.Text("", size=12, color=ft.Colors.RED_700)

        async def submit_request() -> None:
            if not (reason.value or "").strip():
                reason.error = "A reason is required."
                page.update()
                return
            try:
                result = await request((reason.value or "").strip())
            except (ValueError, PermissionError) as exc:
                error.value = str(exc)
                page.update()
                return
            except Exception:
                error.value = "Could not submit the lockout request. Please try again."
                page.update()
                return
            page.pop_dialog()
            await refresh(result)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Request lockout", color=NAVY, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        info_line("Job Card", job.job_card_id),
                        info_line("Equipment", job.equipment),
                        info_line("Equipment ID", job.equipment_id),
                        info_line("Area", job.area),
                        info_line("Requester", user.name if user else "—"),
                        reason,
                        error,
                        ft.Text(
                            "This app records the request; it does not physically isolate equipment.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                    ft.Button(content="Confirm request", on_click=submit_request),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    def show_rejection(title: str, suggested_reason: str = "") -> None:
        async def submit(reason: str) -> Lockout:
            return await state.lockout_service.reject(job.job_card_id, user, reason)

        show_reason_dialog(page, title, submit, refresh, initial_reason=suggested_reason)

    def show_release_request_dialog() -> None:
        reason = ft.TextField(
            label="Reason for release request (required)",
            hint_text="Explain why release is being requested",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        error = ft.Text("", size=12, color=ft.Colors.RED_700)

        async def submit_request() -> None:
            if not (reason.value or "").strip():
                reason.error = "A reason is required."
                page.update()
                return
            try:
                result = await state.lockout_service.request_release(
                    job.job_card_id, user, (reason.value or "").strip()
                )
            except (ValueError, PermissionError) as exc:
                error.value = str(exc)
                page.update()
                return
            except Exception:
                error.value = "Could not submit the release request. Please try again."
                page.update()
                return
            page.pop_dialog()
            await refresh(result)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Request lockout release", color=NAVY, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        info_line("Job Card", job.job_card_id),
                        info_line("Equipment", job.equipment),
                        info_line("Equipment ID", job.equipment_id),
                        info_line("Lockout ID", record.lockout_id if record else "—"),
                        reason,
                        error,
                        ft.Text(
                            "This requests authorised review only. It does not release or physically unlock equipment.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                    ft.Button(content="Submit release request", on_click=submit_request),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    def show_release_approval_dialog() -> None:
        reason = ft.TextField(
            label="Approval notes (optional)",
            hint_text="Record any release context",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        error = ft.Text("", size=12, color=ft.Colors.RED_700)

        async def confirm_release() -> None:
            try:
                result = await state.lockout_service.approve_release(
                    job.job_card_id, user, (reason.value or "").strip()
                )
            except (ValueError, PermissionError) as exc:
                error.value = str(exc)
                page.update()
                return
            except Exception:
                error.value = "Could not record the authorised release. Please try again."
                page.update()
                return
            page.pop_dialog()
            await refresh(result)

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Authorised release confirmation", color=NAVY, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        info_line("Job Card", job.job_card_id),
                        info_line("Equipment", job.equipment),
                        info_line("Equipment ID", job.equipment_id),
                        info_line("Lockout ID", record.lockout_id if record else "—"),
                        info_line("Requester", (record.release_requested_by_name or record.release_requested_by) if record else "—"),
                        info_line("Request reason", record.release_request_reason if record else "—"),
                        reason,
                        error,
                        ft.Text(
                            "Approval is a recorded authorisation only. Follow the approved site procedure before physical release.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                    ft.Button(content="Confirm authorised release", on_click=confirm_release),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    def on_scan_match(equipment: Equipment) -> None:
        scanned_equipment_id[0] = equipment.equipment_id
        scan_feedback.value = f"Scan matched job equipment: {equipment.equipment_id}."
        page.update()

    def on_scan_mismatch(scanned_id: str) -> None:
        mismatch_blocked[0] = True
        scanned_equipment_id[0] = None
        scan_feedback.value = "Equipment mismatch. Lockout cannot continue."
        page.update()
        show_rejection(
            "Equipment mismatch — reject lockout",
            f"Equipment mismatch: scanned {scanned_id}; job card requires {job.equipment_id}.",
        )

    def show_scan_dialog() -> None:
        show_equipment_scan_dialog(page, state, job, on_scan_match, on_scan_mismatch)

    def action_confirmation(title: str, message: str, action: str, label: str, *args) -> None:
        show_confirmation(
            page,
            title=title,
            message=message,
            on_confirm=lambda: change(action, *args),
            confirm_label=label,
        )

    panel: list[ft.Control] = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("LOCKOUT STATUS", size=15, weight=ft.FontWeight.BOLD, color=NAVY),
                ft.Text(
                    status_label,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_900 if current in {
                        LockoutState.LOCKOUT_ACTIVE, LockoutState.REJECTED,
                    } else ft.Colors.TEAL_900,
                ),
            ],
        ),
        ft.Text(
            "The app records authorised confirmations only. It does not physically isolate equipment or verify SCADA.",
            size=12,
            color=MUTED,
        ),
        feedback,
    ]

    if current == LockoutState.NONE:
        if permissions.has_permission(user, REQUEST_LOCKOUT):
            panel.append(primary_button("REQUEST LOCKOUT", show_request_dialog))

    elif current == LockoutState.REQUESTED:
        requester = (record.requested_by_name or record.requested_by) if record else "—"
        panel.extend([
            ft.Text("LOCKOUT REQUEST", size=15, weight=ft.FontWeight.BOLD, color=NAVY),
            info_line("Job Card", job.job_card_id),
            info_line("Equipment", job.equipment),
            info_line("Equipment ID", job.equipment_id),
            info_line("Area", job.area),
            info_line("Requester", requester),
        ])
        if mismatch_blocked[0]:
            panel.append(ft.Text("Equipment mismatch. Lockout cannot continue.", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700))
        panel.append(scan_feedback)
        if permissions.has_permission(user, CONFIRM_EQUIPMENT):
            panel.append(primary_button("SCAN EQUIPMENT", show_scan_dialog))
            if scanned_equipment_id[0] == job.equipment_id and not mismatch_blocked[0]:
                panel.append(primary_button(
                    "CONFIRM SAME EQUIPMENT",
                    lambda: action_confirmation(
                        "Confirm same equipment",
                        f"The resolved QR equipment matches job card equipment {job.equipment_id}. This records your confirmation only.",
                        "equipment", "Confirm same equipment", scanned_equipment_id[0],
                    ),
                ))
            panel.append(secondary_button("REJECT", lambda: show_rejection("Reject lockout request")))
        else:
            panel.append(ft.Text("Awaiting an authorised equipment confirmation.", size=13, color=MUTED))

    elif current == LockoutState.EQUIPMENT_CONFIRMED:
        panel.extend([
            ft.Text("SCADA STOP CONFIRMATION", size=15, weight=ft.FontWeight.BOLD, color=NAVY),
            info_line("Equipment", job.equipment),
            info_line("Job Card", job.job_card_id),
            ft.Text(
                "Confirm that the equipment has been stopped on SCADA according to the approved site procedure.",
                size=13,
                color=NAVY,
            ),
            ft.Text("This records your confirmation only; the app does not connect to or verify SCADA.", size=12, color=MUTED),
        ])
        if permissions.has_permission(user, CONFIRM_SCADA_STOP):
            panel.extend([
                primary_button(
                    "CONFIRM STOP ON SCADA",
                    lambda: action_confirmation(
                        "Confirm stop on SCADA",
                        "Confirm that you completed the approved site check. The app records your statement; it has not verified SCADA.",
                        "scada", "Record SCADA confirmation",
                    ),
                ),
                secondary_button("CANNOT CONFIRM", lambda: show_rejection("SCADA stop cannot be confirmed")),
            ])

    elif current == LockoutState.SCADA_STOP_CONFIRMED:
        panel.extend([
            ft.Text("PHYSICAL LOCKOUT", size=15, weight=ft.FontWeight.BOLD, color=NAVY),
            info_line("Equipment", job.equipment),
            info_line("Job Card", job.job_card_id),
            ft.Text(
                "Confirm that the equipment has been physically isolated/locked out according to the approved site procedure.",
                size=13,
                color=NAVY,
            ),
            ft.Text("Only the authorised in-person action can isolate equipment. This app records a confirmation only.", size=12, color=MUTED),
        ])
        if permissions.has_permission(user, CONFIRM_PHYSICAL_LOCKOUT):
            panel.extend([
                primary_button(
                    "CONFIRM LOCKOUT",
                    lambda: action_confirmation(
                        "Confirm physical lockout",
                        "Only continue after physical isolation/lockout has been completed in person under the approved site procedure.",
                        "physical", "Record physical confirmation",
                    ),
                ),
                secondary_button("REJECT", lambda: show_rejection("Reject physical lockout confirmation")),
            ])

    elif current == LockoutState.LOCKOUT_ACTIVE:
        panel.append(ft.Text("LOCKOUT ACTIVE", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900))
        panel.append(ft.Text("Required confirmations are recorded. Maintain physical isolation under the approved site procedure.", size=13, color=NAVY))
        if permissions.has_permission(user, REQUEST_LOCKOUT_RELEASE):
            panel.append(primary_button("REQUEST RELEASE", show_release_request_dialog))

    elif current == LockoutState.RELEASE_REQUESTED:
        panel.extend([
            ft.Text("AUTHORISED RELEASE CONFIRMATION", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_900),
            info_line("Job Card", job.job_card_id),
            info_line("Equipment", job.equipment),
            info_line("Equipment ID", job.equipment_id),
            info_line("Lockout ID", record.lockout_id if record else "—"),
            info_line("Requester", (record.release_requested_by_name or record.release_requested_by) if record else "—"),
            info_line("Requested at", record.release_requested_at if record else "—"),
            info_line("Reason", record.release_request_reason if record else "—"),
            ft.Text("Release approval is pending. Do not remove physical isolation based only on this app.", size=13, color=MUTED),
        ])
        if permissions.has_permission(user, APPROVE_LOCKOUT_RELEASE):
            panel.append(primary_button("AUTHORISE RELEASE", show_release_approval_dialog))

    elif current == LockoutState.REJECTED:
        panel.append(ft.Text(record.rejection_reason if record and record.rejection_reason else "Workflow rejected; follow up with the authorised approver.", size=13, color=ft.Colors.RED_700))
    elif current == LockoutState.RELEASED:
        panel.append(ft.Text("Release approval recorded. Follow site procedure before returning equipment to service.", size=13, color=MUTED))

    panel.extend(audit_history(record))

    return ft.Container(
        padding=14,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(tight=True, spacing=10, controls=panel),
    )
