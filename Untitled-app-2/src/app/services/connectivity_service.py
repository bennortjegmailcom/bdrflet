"""Connectivity status facade; production connectivity signals can replace the demo provider."""

from enum import Enum


class ConnectivityStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    SYNCING = "SYNCING"
    SYNC_ERROR = "SYNC ERROR"


class ConnectivityService:
    def __init__(self, initially_online: bool = True):
        self._status = ConnectivityStatus.ONLINE if initially_online else ConnectivityStatus.OFFLINE
        self._last_error = ""

    @property
    def status(self) -> ConnectivityStatus:
        return self._status

    @property
    def last_error(self) -> str:
        return self._last_error

    async def set_online(self, online: bool) -> None:
        if self._status != ConnectivityStatus.SYNCING:
            self._status = ConnectivityStatus.ONLINE if online else ConnectivityStatus.OFFLINE
        if online:
            self._last_error = ""

    async def begin_sync(self) -> None:
        self._status = ConnectivityStatus.SYNCING
        self._last_error = ""

    async def sync_failed(self, message: str) -> None:
        self._status = ConnectivityStatus.SYNC_ERROR
        self._last_error = message

    async def sync_finished(self) -> None:
        self._status = ConnectivityStatus.ONLINE
        self._last_error = ""
