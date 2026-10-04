"""Reusable equipment search and explicitly confirmed QR identification UI."""

import flet as ft

from app.components.action_buttons import secondary_button
from app.models.equipment import Equipment
from app.services.equipment_identification_service import (
    EquipmentIdentificationService,
    EquipmentScanResult,
)
from app.services.equipment_service import EquipmentService
from app.theme import MUTED, NAVY, TEAL


def equipment_selector(
    page: ft.Page,
    equipment_service: EquipmentService,
    identification_service: EquipmentIdentificationService,
    current_equipment_id: ft.TextField,
    on_equipment_selected,
) -> ft.Control:
    search_field = ft.TextField(label="Search equipment", hint_text="Name, code, area, or workgroup")
    qr_field = ft.TextField(label="QR identifier", hint_text="Demo: QR-CV-204")
    search_results = ft.Column(tight=True, spacing=4)
    message = ft.Text("Camera scanning can be connected through the QR scanner service.", size=12, color=MUTED)
    scan_result: list[EquipmentScanResult | None] = [None]

    def choose_equipment(equipment: Equipment) -> None:
        on_equipment_selected(equipment)
        search_results.controls.clear()
        message.value = f"Selected {equipment.equipment_code} · {equipment.description}"
        message.color = TEAL
        page.update()

    def equipment_tile(item: Equipment) -> ft.Control:
        return ft.Container(
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_100)),
            content=ft.ListTile(
                title=ft.Text(f"{item.equipment_code} · {item.description}"),
                subtitle=ft.Text(f"{item.area} · {item.plant} · {item.workgroup}"),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                on_click=lambda: choose_equipment(item),
            ),
        )

    async def search() -> None:
        matches = await equipment_service.search(search_field.value or "")
        search_results.controls = [equipment_tile(item) for item in matches]
        if not matches:
            search_results.controls = [ft.Text("No active equipment found.", size=12, color=MUTED)]
        page.update()

    async def resolve_qr() -> None:
        result = await identification_service.scan_and_resolve(
            qr_field.value,
            current_equipment_id.value,
        )
        scan_result[0] = result
        if result.qr_identifier is None:
            message.value = "Enter a QR identifier to resolve equipment."
            message.color = ft.Colors.RED_700
        elif result.unknown:
            message.value = f"Unknown QR code: {result.qr_identifier}. Equipment was not selected."
            message.color = ft.Colors.RED_700
        elif result.equipment is not None and result.mismatch:
            current_id = result.current_equipment_id or "(not set)"
            message.value = (
                f"Equipment mismatch: current ID {current_id}; QR resolves to "
                f"{result.equipment.equipment_code} ({result.equipment.equipment_id}) in "
                f"{result.equipment.area}, {result.equipment.plant}. Confirm the replacement explicitly."
            )
            message.color = ft.Colors.RED_700
        elif result.equipment is not None:
            message.value = (
                f"QR resolved: {result.equipment.equipment_code} · "
                f"{result.equipment.description} · {result.equipment.area} · "
                f"{result.equipment.workgroup}. Confirm to associate it."
            )
            message.color = NAVY
        page.update()

    def confirm_qr() -> None:
        result = scan_result[0]
        if result is None or result.equipment is None or result.unknown:
            return
        choose_equipment(result.equipment)
        qr_field.value = result.qr_identifier or ""
        message.value = f"Confirmed {result.equipment.equipment_code} for this report."
        message.color = TEAL
        page.update()

    def qr_confirm_control() -> ft.Control:
        result = scan_result[0]
        if result is None or result.equipment is None or result.unknown:
            return ft.Container()
        label = "Use scanned equipment instead" if result.mismatch else "Confirm QR equipment"
        return secondary_button(label, confirm_qr, icon=ft.Icons.QR_CODE_SCANNER)

    qr_confirm = ft.Container()

    async def resolve_and_refresh() -> None:
        await resolve_qr()
        qr_confirm.content = qr_confirm_control()
        page.update()

    return ft.Container(
        padding=16,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=14,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text("Equipment identification", size=16, weight=ft.FontWeight.BOLD, color=NAVY),
                ft.Text("Search the catalogue or resolve a QR identifier before confirming equipment.", size=12, color=MUTED),
                search_field,
                secondary_button("Search equipment", search, icon=ft.Icons.SEARCH),
                search_results,
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                qr_field,
                secondary_button("Resolve QR code", resolve_and_refresh, icon=ft.Icons.QR_CODE_SCANNER),
                qr_confirm,
                message,
            ],
        ),
    )
