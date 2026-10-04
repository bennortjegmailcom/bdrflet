"""Breakdown report models shared by screens and service adapters."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReportAttachment:
    filename: str
    content: bytes = field(default=b"", repr=False)
    media_type: str = "application/octet-stream"


@dataclass(frozen=True)
class ReportHistoryEntry:
    timestamp: str
    message: str
    actor: str


@dataclass(frozen=True)
class BreakdownReportDraft:
    equipment: str
    equipment_id: str
    area: str
    problem_description: str
    priority: str
    workgroup: str
    photo: ReportAttachment | None = None
    additional_photos: tuple[ReportAttachment, ...] = ()
    audio: ReportAttachment | None = None
    location: str | None = None


@dataclass(frozen=True)
class ReportSubmissionResult:
    report_reference: str
    job_reference: str
