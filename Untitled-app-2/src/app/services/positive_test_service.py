"""Positive-test application service over a replaceable BDR API provider."""

from datetime import datetime
from typing import Protocol

from app.models.job_card import JobCard
from app.models.lockout import LockoutState
from app.models.positive_test import PositiveTest
from app.models.report import ReportAttachment
from app.models.user import User
from app.services.lockout_service import LockoutService
from app.services.permission_service import PermissionService, START_POSITIVE_TEST


class PositiveTestApiProvider(Protocol):
    async def get_job_card(self, job_card_id: str) -> JobCard | None: ...

    async def get_positive_tests(self, job_card_id: str) -> tuple[PositiveTest, ...]: ...

    async def create_positive_test(self, test: PositiveTest) -> PositiveTest: ...


class PositiveTestService:
    """Enforce active-lockout and authorization checks before recording tests."""

    def __init__(
        self,
        provider: PositiveTestApiProvider,
        lockout_service: LockoutService,
        permissions: PermissionService,
        audit_service=None,
    ):
        self._provider = provider
        self._lockout_service = lockout_service
        self._permissions = permissions
        self._audit_service = audit_service

    async def get_for_job_card(self, job_card_id: str) -> tuple[PositiveTest, ...]:
        return await self._provider.get_positive_tests(job_card_id)

    async def start(
        self,
        job_card_id: str,
        user: User | None,
        result: str,
        notes: str = "",
        photos: tuple[ReportAttachment, ...] = (),
    ) -> PositiveTest:
        if user is None or not self._permissions.has_permission(user, START_POSITIVE_TEST):
            raise PermissionError("Your role is not authorised to record a positive test.")
        result = result.strip()
        if not result:
            raise ValueError("A test result is required.")
        lockout = await self._lockout_service.get_for_job_card(job_card_id)
        if lockout is None or lockout.status != LockoutState.LOCKOUT_ACTIVE:
            raise ValueError(
                "This positive test cannot proceed until the required lockout workflow has been completed."
            )
        job = await self._provider.get_job_card(job_card_id)
        if job is None:
            raise ValueError("Job card is no longer available.")
        if lockout.equipment_id.casefold() != job.equipment_id.casefold():
            raise ValueError("Lockout equipment does not match the job card equipment.")
        timestamp = datetime.now().strftime("%d %b %Y · %H:%M")
        sequence = len(await self._provider.get_positive_tests(job_card_id)) + 1
        test = PositiveTest(
            positive_test_id=f"PT-{job_card_id}-{sequence:02d}",
            user_id=user.id,
            user_name=user.name,
            timestamp=timestamp,
            job_card_id=job.job_card_id,
            equipment=job.equipment,
            equipment_id=job.equipment_id,
            lockout_id=lockout.lockout_id,
            result=result,
            notes=notes.strip(),
            photos=photos,
        )
        saved = await self._provider.create_positive_test(test)
        if self._audit_service is not None:
            await self._audit_service.record(
                job_card_id=job.job_card_id,
                lockout_id=lockout.lockout_id,
                event_type="POSITIVE_TEST_COMPLETED",
                previous_state="STARTED",
                new_state="COMPLETED",
                user=user.name,
                timestamp=timestamp,
                equipment=job.equipment,
                reason=result,
            )
        return saved
