from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Authenticated BDR user; username stores the account username or email."""

    id: str
    name: str
    username: str
    role: str
    workgroup: str
    active: bool

    @property
    def email(self) -> str:
        """Compatibility alias for screens that display an email address."""
        return self.username

    @property
    def site(self) -> str:
        """Compatibility alias for older profile UI; prefer workgroup."""
        return self.workgroup
