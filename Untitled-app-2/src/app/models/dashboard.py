from dataclasses import dataclass


@dataclass(frozen=True)
class ActivityItem:
    title: str
    asset: str
    age: str
    status: str


@dataclass(frozen=True)
class DashboardSummary:
    open_reports: int
    awaiting_review: int
    resolved_this_week: int
    recent_activity: tuple[ActivityItem, ...]
