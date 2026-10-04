"""Backend boundary for BDR data; replace the demo implementation when an API exists."""

from typing import Protocol

from app.models.dashboard import ActivityItem, DashboardSummary
from app.models.work_items import BdrNotification, BreakdownReport, JobCard
from app.services.demo_repository import MockBdrRepository


class BdrService(Protocol):
    async def get_dashboard_summary(self) -> DashboardSummary:
        """Fetch the signed-in user's dashboard summary."""

    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        """Fetch breakdown reports available to the signed-in user."""

    async def get_job_cards(self) -> tuple[JobCard, ...]:
        """Fetch job cards available to the signed-in user."""

    async def get_notifications(self) -> tuple[BdrNotification, ...]:
        """Fetch notifications available to the signed-in user."""


class DemoBdrService:
    """Seeded dashboard and notification content used until a BDR backend is connected."""

    def __init__(self):
        self._repository = MockBdrRepository()

    async def get_dashboard_summary(self) -> DashboardSummary:
        return DashboardSummary(
            open_reports=8,
            awaiting_review=3,
            resolved_this_week=12,
            recent_activity=(
                ActivityItem(
                    title="Conveyor belt vibration",
                    asset="CV-204 · Packing line",
                    age="18 min ago",
                    status="New",
                ),
                ActivityItem(
                    title="Pump pressure below range",
                    asset="PU-018 · Utilities",
                    age="1 hr ago",
                    status="In review",
                ),
                ActivityItem(
                    title="Motor coupling inspection",
                    asset="MT-112 · Process hall",
                    age="Yesterday",
                    status="Assigned",
                ),
            ),
        )

    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        return await self._repository.get_reports()

    async def get_job_cards(self) -> tuple[JobCard, ...]:
        return await self._repository.get_job_cards()

    async def get_notifications(self) -> tuple[BdrNotification, ...]:
        return (
            BdrNotification("New breakdown report", "BR-2481 was reported for CV-204.", "18 min ago", True),
            BdrNotification("Job card assigned", "JC-3908 is waiting for your attention.", "42 min ago", True),
            BdrNotification("Report updated", "BR-2476 moved to In review.", "2 hr ago"),
        )
