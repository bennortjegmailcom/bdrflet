"""Job card domain model and supported BDR work statuses."""

from dataclasses import dataclass
from enum import Enum

from app.models.report import ReportAttachment


class JobCardStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    AT_EQUIPMENT = "AT_EQUIPMENT"
    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"
    WORK_COMPLETE = "WORK_COMPLETE"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True)
class JobCard:
    job_card_id: str
    report_id: str
    equipment: str
    equipment_id: str
    area: str
    problem_description: str
    priority: str
    workgroup: str
    assigned_worker: str
    status: str
    created_at: str
    updated_at: str
    notes: tuple[str, ...] = ()
    photos: tuple[ReportAttachment, ...] = ()
    lockout_status: str = "NONE"
    due_at: str = ""
    lockout_id: str | None = None

    @property
    def reference(self) -> str:
        return self.job_card_id

    @property
    def title(self) -> str:
        return self.problem_description

    @property
    def asset(self) -> str:
        return f"{self.equipment} · {self.equipment_id}"

    @property
    def due(self) -> str:
        return self.due_at or self.updated_at
