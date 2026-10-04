"""Replaceable QR scanner contract with a preview-friendly mock implementation."""

from typing import Protocol


class QRScanner(Protocol):
    async def scan(self, entered_value: str | None = None) -> str | None:
        """Return the scanned QR payload, or None when scanning is cancelled."""


class MockQRScanner:
    """Mock scanner that accepts a typed QR payload in preview/demo mode.

    A native camera scanner can replace this adapter without changing screens.
    """

    async def scan(self, entered_value: str | None = None) -> str | None:
        value = (entered_value or "").strip()
        return value or None
