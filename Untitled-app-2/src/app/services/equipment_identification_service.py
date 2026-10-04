"""Coordinates QR scanning, equipment lookup, and explicit mismatch detection."""

from dataclasses import dataclass

from app.models.equipment import Equipment
from app.services.equipment_service import EquipmentService
from app.services.qr_scanner import QRScanner


@dataclass(frozen=True)
class EquipmentScanResult:
    qr_identifier: str | None
    equipment: Equipment | None
    unknown: bool
    mismatch: bool
    current_equipment_id: str | None = None


class EquipmentIdentificationService:
    def __init__(self, scanner: QRScanner, equipment_service: EquipmentService):
        self._scanner = scanner
        self._equipment_service = equipment_service

    async def scan_and_resolve(
        self,
        entered_value: str | None,
        current_equipment_id: str | None = None,
    ) -> EquipmentScanResult:
        qr_identifier = await self._scanner.scan(entered_value)
        if qr_identifier is None:
            return EquipmentScanResult(None, None, unknown=False, mismatch=False, current_equipment_id=current_equipment_id)
        equipment = await self._equipment_service.resolve_qr(qr_identifier)
        if equipment is None:
            return EquipmentScanResult(qr_identifier, None, unknown=True, mismatch=False, current_equipment_id=current_equipment_id)
        mismatch = bool(
            current_equipment_id
            and current_equipment_id.strip().casefold() not in {
                equipment.equipment_id.casefold(),
                equipment.equipment_code.casefold(),
            }
        )
        return EquipmentScanResult(qr_identifier, equipment, unknown=False, mismatch=mismatch, current_equipment_id=current_equipment_id)
