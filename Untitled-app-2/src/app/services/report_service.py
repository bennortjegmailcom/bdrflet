"""Report application service backed by a replaceable BDR API/repository."""

from typing import Protocol

from app.models.report import BreakdownReportDraft, ReportSubmissionResult
from app.models.work_items import BreakdownReport


class ReportApiProvider(Protocol):
    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        """Return reports authorized for the signed-in user."""

    async def get_report(self, report_id: str) -> BreakdownReport | None:
        """Return one authorized report by its identifier."""

    async def submit_report(self, draft: BreakdownReportDraft) -> ReportSubmissionResult:
        """Submit a report and return its report/job references."""


class ReportService:
    """Business-facing report service; screens never access repositories directly."""

    def __init__(self, provider: ReportApiProvider, audit_service=None):
        self._provider = provider
        self._audit_service = audit_service

    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        return await self._provider.get_reports()

    async def get_report(self, report_id: str) -> BreakdownReport | None:
        return await self._provider.get_report(report_id)

    async def submit_report(self, draft: BreakdownReportDraft, user=None) -> ReportSubmissionResult:
        result = await self._provider.submit_report(draft)
        if self._audit_service is not None:
            actor = user.name if user is not None else "Current user"
            await self._audit_service.record(
                job_card_id=result.job_reference,
                event_type="REPORT_CREATED",
                user=actor,
                equipment=draft.equipment,
                new_state="New",
            )
            await self._audit_service.record(
                job_card_id=result.job_reference,
                event_type="JOB_CREATED",
                user=actor,
                equipment=draft.equipment,
                previous_state="NONE",
                new_state="OPEN",
            )
        return result


class MockReportApiProvider:
    """Backward-compatible named mock provider backed by the shared demo repository."""

    def __init__(self, first_reference_number: int = 1001, repository=None):
        if repository is None:
            from app.services.demo_repository import MockBdrRepository

            repository = MockBdrRepository()
            repository._next_report_number = first_reference_number
        self._repository = repository

    async def get_reports(self) -> tuple[BreakdownReport, ...]:
        return await self._repository.get_reports()

    async def get_report(self, report_id: str) -> BreakdownReport | None:
        return await self._repository.get_report(report_id)

    async def submit_report(self, draft: BreakdownReportDraft) -> ReportSubmissionResult:
        return await self._repository.submit_report(draft)
