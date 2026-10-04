"""Authentication contract and in-memory demo provider for BDR Mobile."""

from typing import Protocol

from app.models.user import User


DEMO_USER = User(
    id="demo-maintenance-supervisor-01",
    name="Jordan Lee",
    username="jordan.lee@northplant.example",
    role="Maintenance Supervisor",
    workgroup="North Plant Maintenance",
    active=True,
)

MOCK_USERS = (
    User("mock-reporter-01", "Riley Morgan", "riley.reporter@demo.example", "Reporter", "North Plant", True),
    User("mock-scheduler-01", "Casey Patel", "casey.scheduler@demo.example", "Scheduler", "North Plant", True),
    User("mock-coordinator-01", "Taylor Chen", "taylor.coordinator@demo.example", "Coordinator", "North Plant", True),
    User("mock-shift-foreman-01", "Morgan Ellis", "morgan.shiftforeman@demo.example", "Maintenance Shift Foreman", "North Plant", True),
    User("mock-foreman-01", "Avery Brooks", "avery.foreman@demo.example", "Foreman", "North Plant", True),
    User("mock-artisan-01", "Jamie Singh", "jamie.artisan@demo.example", "Artisan", "North Plant", True),
    User("mock-guest-01", "Alex Guest", "alex.guest@demo.example", "Guest", "North Plant", True),
    User("mock-admin-01", "Sam Admin", "sam.admin@demo.example", "Admin", "BDR Demo", True),
)


class AuthService(Protocol):
    async def login(self, username: str | None = None, password: str | None = None) -> User | None:
        """Sign in and return the authenticated user, or None if rejected."""

    async def logout(self) -> None:
        """End the current session."""

    async def get_current_user(self) -> User | None:
        """Return the current authenticated user, if any."""

    async def refresh_session(self) -> User | None:
        """Validate or renew the current session and return its user."""

    async def is_authenticated(self) -> bool:
        """Return whether an active authenticated session exists."""


class MockAuthService:
    """In-memory demo provider; it does not validate production credentials.

    `login()` without a username selects the normal demo account. Supplying one
    selects a seeded persona for testing role-specific UI. Passwords are not
    checked by this mock provider.
    """

    def __init__(self, demo_user: User = DEMO_USER):
        self._demo_user = demo_user
        self._users_by_username = {user.username.casefold(): user for user in MOCK_USERS}
        self._users_by_username[demo_user.username.casefold()] = demo_user
        self._current_user: User | None = None

    async def login(self, username: str | None = None, password: str | None = None) -> User | None:
        if username is None:
            selected_user = self._demo_user
        else:
            selected_user = self._users_by_username.get(username.strip().casefold())
        self._current_user = selected_user if selected_user is not None and selected_user.active else None
        return self._current_user

    async def logout(self) -> None:
        self._current_user = None

    async def get_current_user(self) -> User | None:
        if self._current_user is not None and self._current_user.active:
            return self._current_user
        return None

    async def refresh_session(self) -> User | None:
        return await self.get_current_user()

    async def is_authenticated(self) -> bool:
        return await self.get_current_user() is not None
