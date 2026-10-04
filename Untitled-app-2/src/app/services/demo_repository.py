"""In-memory repository implementing the replaceable BDR API boundary."""

from dataclasses import replace
from datetime import datetime

from app.models.equipment import Equipment
from app.models.job_card import JobCard, JobCardStatus
from app.models.lockout import Lockout, LockoutState
from app.models.positive_test import PositiveTest
from app.models.report import (
    BreakdownReportDraft,
    ReportAttachment,
    ReportHistoryEntry,
    ReportSubmissionResult,
)
from app.models.work_items import BreakdownReport


def _now_label() -> str:
    return datetime.now().strftime("%d %b %Y · %H:%M")


class MockBdrRepository:
    """Seeded local API substitute shared by the report, job, and equipment services."""

    def __init__(self):
        self._equipment = (
            Equipment("EQ-0204", "CV-204", "Packing line conveyor", "Packing line", "North Plant", "Packaging", "North Plant Maintenance", "QR-CV-204", "PKG.CV204", True),
            Equipment("EQ-0018", "PU-018", "Utilities transfer pump", "Utilities", "North Plant", "Utilities", "North Plant Maintenance", "QR-PU-018", "UTIL.PU018", True),
            Equipment("EQ-0112", "MT-112", "Process hall motor", "Process hall", "North Plant", "Processing", "North Plant Maintenance", "QR-MT-112", "PROC.MT112", True),
            Equipment("EQ-0317", "MX-317", "Blend tank agitator", "Mixing bay", "North Plant", "Processing", "North Plant Maintenance", "QR-MX-317", "MIX.MX317", True),
        )
        self._reports = [
            BreakdownReport(
                reference="BR-2481", title="Conveyor belt vibration", asset="Packing line conveyor · CV-204",
                age="18 min ago", status="New", priority="High", created_at="04 Oct 2026 · 10:12",
                equipment="Packing line conveyor", equipment_id="EQ-0204", area="Packing line",
                workgroup="North Plant Maintenance", assigned_workgroup="North Plant Maintenance",
                photos=(ReportAttachment("CV-204-belt.jpg", b"", "image/jpeg"),),
                history=(ReportHistoryEntry("04 Oct 2026 · 10:12", "Breakdown report submitted", "Riley Morgan"),),
            ),
            BreakdownReport(
                reference="BR-2476", title="Pump pressure below range", asset="Utilities transfer pump · PU-018",
                age="1 hr ago", status="In review", priority="Urgent", created_at="04 Oct 2026 · 09:24",
                equipment="Utilities transfer pump", equipment_id="EQ-0018", area="Utilities",
                workgroup="North Plant Maintenance", assigned_workgroup="North Plant Maintenance",
                audio_attachments=(ReportAttachment("pump-pressure-note.m4a", b"", "audio/mp4"),),
                history=(
                    ReportHistoryEntry("04 Oct 2026 · 09:24", "Breakdown report submitted", "Riley Morgan"),
                    ReportHistoryEntry("04 Oct 2026 · 09:41", "Assigned for maintenance review", "Casey Patel"),
                ),
            ),
            BreakdownReport(
                reference="BR-2462", title="Motor coupling inspection", asset="Process hall motor · MT-112",
                age="Yesterday", status="Assigned", priority="Normal", created_at="03 Oct 2026 · 15:36",
                equipment="Process hall motor", equipment_id="EQ-0112", area="Process hall",
                workgroup="North Plant Maintenance", assigned_workgroup="Electrical Maintenance",
                history=(ReportHistoryEntry("03 Oct 2026 · 15:36", "Inspection request assigned", "Morgan Ellis"),),
            ),
        ]
        self._job_cards = [
            JobCard(
                "JC-3908", "BR-2481", "Packing line conveyor", "EQ-0204", "Packing line",
                "Conveyor belt vibration", "High", "North Plant Maintenance", "Jamie Singh",
                JobCardStatus.ASSIGNED.value, "04 Oct 2026 · 10:12", "04 Oct 2026 · 10:28",
                notes=("Check drive-end bearing and belt tracking.",),
                photos=(ReportAttachment("CV-204-belt.jpg", b"", "image/jpeg"),), due_at="Today · 14:00",
            ),
            JobCard(
                "JC-3891", "BR-2476", "Utilities transfer pump", "EQ-0018", "Utilities",
                "Pump pressure below range", "Urgent", "North Plant Maintenance", "Avery Brooks",
                JobCardStatus.WORK_IN_PROGRESS.value, "04 Oct 2026 · 08:45", "04 Oct 2026 · 09:30",
                notes=("Initial pressure check completed; inspect suction filter.",), due_at="Today · 16:30",
            ),
            JobCard(
                "JC-3860", "BR-2462", "Process hall motor", "EQ-0112", "Process hall",
                "Motor coupling inspection", "Normal", "Electrical Maintenance", "Unassigned",
                JobCardStatus.OPEN.value, "03 Oct 2026 · 15:36", "03 Oct 2026 · 15:36",
                due_at="Tomorrow",
            ),
        ]
        self._lockouts: dict[str, Lockout] = {}
        self._positive_tests: dict[str, list[PositiveTest]] = {}
        self._next_report_number = 1001
        self._next_job_number = 2001

    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        return tuple(self._reports)

    async def get_report(self, report_id: str) -> BreakdownReport | None:
        return next((report for report in self._reports if report.reference == report_id), None)

    async def submit_report(self, draft: BreakdownReportDraft) -> ReportSubmissionResult:
        report_reference = f"BDR-DEMO-{self._next_report_number}"
        job_reference = f"JC-DEMO-{self._next_job_number}"
        self._next_report_number += 1
        self._next_job_number += 1
        created_at = _now_label()
        photos = tuple(item for item in (draft.photo, *draft.additional_photos) if item is not None)
        audio = (draft.audio,) if draft.audio is not None else ()
        report = BreakdownReport(
            reference=report_reference,
            title=draft.problem_description,
            asset=f"{draft.equipment} · {draft.equipment_id}",
            age="Just now",
            status="New",
            priority=draft.priority,
            created_at=created_at,
            equipment=draft.equipment,
            equipment_id=draft.equipment_id,
            area=draft.area,
            workgroup=draft.workgroup,
            assigned_workgroup=draft.workgroup,
            location=draft.location or "",
            photos=photos,
            audio_attachments=audio,
            attachments=photos + audio,
            history=(ReportHistoryEntry(created_at, "Breakdown report submitted", "Current user"),),
        )
        self._reports.insert(0, report)
        self._job_cards.insert(
            0,
            JobCard(
                job_card_id=job_reference,
                report_id=report_reference,
                equipment=draft.equipment,
                equipment_id=draft.equipment_id,
                area=draft.area,
                problem_description=draft.problem_description,
                priority=draft.priority,
                workgroup=draft.workgroup,
                assigned_worker="Unassigned",
                status=JobCardStatus.OPEN.value,
                created_at=created_at,
                updated_at=created_at,
                photos=photos,
                due_at="Unscheduled",
            ),
        )
        return ReportSubmissionResult(report_reference, job_reference)

    async def get_job_cards(self) -> tuple[JobCard, ...]:
        return tuple(self._job_cards)

    async def get_job_card(self, job_card_id: str) -> JobCard | None:
        return next((card for card in self._job_cards if card.job_card_id == job_card_id), None)

    async def get_lockout_for_job(self, job_card_id: str) -> Lockout | None:
        return next(
            (lockout for lockout in self._lockouts.values() if lockout.job_card_id == job_card_id),
            None,
        )

    async def create_lockout(self, lockout: Lockout) -> Lockout:
        if await self.get_job_card(lockout.job_card_id) is None:
            raise ValueError("Job card is no longer available.")
        if await self.get_lockout_for_job(lockout.job_card_id) is not None:
            raise ValueError("A lockout request already exists for this job card.")
        if lockout.status != LockoutState.REQUESTED:
            raise ValueError("New lockout requests must begin in REQUESTED state.")
        return await self.save_lockout(lockout)

    async def save_lockout(self, lockout: Lockout) -> Lockout:
        if lockout.lockout_id not in self._lockouts:
            if lockout.status != LockoutState.REQUESTED:
                raise ValueError("Lockout record does not exist.")
        for index, card in enumerate(self._job_cards):
            if card.job_card_id == lockout.job_card_id:
                self._lockouts[lockout.lockout_id] = lockout
                self._job_cards[index] = replace(
                    card,
                    lockout_id=lockout.lockout_id,
                    lockout_status=lockout.status.value,
                    updated_at=_now_label(),
                )
                return lockout
        raise ValueError("Job card is no longer available.")

    async def get_positive_tests(self, job_card_id: str) -> tuple[PositiveTest, ...]:
        if await self.get_job_card(job_card_id) is None:
            raise ValueError("Job card is no longer available.")
        return tuple(self._positive_tests.get(job_card_id, ()))

    async def create_positive_test(self, test: PositiveTest) -> PositiveTest:
        job = await self.get_job_card(test.job_card_id)
        lockout = await self.get_lockout_for_job(test.job_card_id)
        if job is None:
            raise ValueError("Job card is no longer available.")
        if lockout is None or lockout.status != LockoutState.LOCKOUT_ACTIVE:
            raise ValueError("Positive tests require an active lockout.")
        if test.equipment_id.casefold() != job.equipment_id.casefold():
            raise ValueError("Positive-test equipment does not match the job card.")
        if test.lockout_id != lockout.lockout_id:
            raise ValueError("Positive-test lockout does not match the active lockout.")
        self._positive_tests.setdefault(test.job_card_id, []).append(test)
        return test

    async def add_job_note(self, job_card_id: str, note: str) -> JobCard | None:
        for index, card in enumerate(self._job_cards):
            if card.job_card_id == job_card_id:
                updated = replace(card, notes=(*card.notes, note), updated_at=_now_label())
                self._job_cards[index] = updated
                return updated
        return None

    async def search_equipment(self, query: str) -> tuple[Equipment, ...]:
        query = query.strip().casefold()
        active = (equipment for equipment in self._equipment if equipment.active)
        if not query:
            return tuple(active)
        return tuple(
            equipment
            for equipment in active
            if query in " ".join((
                equipment.equipment_id,
                equipment.equipment_code,
                equipment.description,
                equipment.area,
                equipment.plant,
                equipment.department,
                equipment.workgroup,
                equipment.qr_identifier,
                equipment.scada_tag,
            )).casefold()
        )

    async def get_equipment(self, equipment_id: str) -> Equipment | None:
        query = equipment_id.strip().casefold()
        return next(
            (
                equipment for equipment in self._equipment
                if equipment.equipment_id.casefold() == query or equipment.equipment_code.casefold() == query
            ),
            None,
        )

    async def resolve_equipment_qr(self, qr_identifier: str) -> Equipment | None:
        query = qr_identifier.strip().casefold()
        if not query:
            return None
        return next(
            (
                equipment for equipment in self._equipment
                if equipment.active and equipment.qr_identifier.casefold() == query
            ),
            None,
        )
