from dataclasses import dataclass

from app.models.job_card import JobCard
from app.models.report import ReportAttachment, ReportHistoryEntry


@dataclass(frozen=True)
class BreakdownReport:
    """Report record, retaining the original summary fields for compatibility."""

    reference: str
    title: str
    asset: str
    age: str
    status: str
    priority: str = "Normal"
    created_at: str = ""
    equipment: str = ""
    equipment_id: str = ""
    area: str = ""
    workgroup: str = ""
    assigned_workgroup: str = ""
    location: str = ""
    photos: tuple[ReportAttachment, ...] = ()
    audio_attachments: tuple[ReportAttachment, ...] = ()
    attachments: tuple[ReportAttachment, ...] = ()
    history: tuple[ReportHistoryEntry, ...] = ()

    @property
    def problem_description(self) -> str:
        return self.title


@dataclass(frozen=True)
class BdrNotification:
    title: str
    message: str
    age: str
    unread: bool = False
    notification_id: str = ""
    kind: str = "JOB_UPDATED"
    job_card_id: str = ""
    event_id: str = ""
