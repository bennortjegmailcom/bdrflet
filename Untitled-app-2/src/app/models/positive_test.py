"""Positive-test record captured after the controlled lockout is active."""

from dataclasses import dataclass

from app.models.report import ReportAttachment


@dataclass(frozen=True)
class PositiveTest:
    positive_test_id: str
    user_id: str
    user_name: str
    timestamp: str
    job_card_id: str
    equipment: str
    equipment_id: str
    lockout_id: str
    result: str
    notes: str = ""
    photos: tuple[ReportAttachment, ...] = ()
