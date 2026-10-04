from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    name: str
    role: str
    site: str
    email: str


DEMO_PROFILE = UserProfile(
    name="Jordan Lee",
    role="Maintenance Supervisor",
    site="North Plant",
    email="jordan.lee@northplant.example",
)
