"""Optional photo and audio attachment picker for report forms."""

import flet as ft

from app.models.report import ReportAttachment
from app.theme import MUTED, NAVY


class ReportUploadPicker:
    def __init__(self, page: ft.Page, file_picker: ft.FilePicker):
        self._page = page
        self._file_picker = file_picker
        self._photo_files: list = []
        self._additional_photo_files: list = []
        self._audio_files: list = []
        self.photo_status = ft.Text("No photo selected", size=12, color=MUTED)
        self.additional_status = ft.Text("No additional photos selected", size=12, color=MUTED)
        self.audio_status = ft.Text("No audio selected", size=12, color=MUTED)
        self.control = ft.Column(
            tight=True,
            spacing=12,
            controls=[
                ft.Text("Attachments (optional)", size=17, weight=ft.FontWeight.BOLD, color=NAVY),
                self._section(
                    "Photo", "Attach a photo of the equipment or fault.",
                    "Choose photo", ft.Icons.ADD_A_PHOTO, self._select_photo, self.photo_status,
                ),
                self._section(
                    "Additional photos", "Attach any other helpful images.",
                    "Choose photos", ft.Icons.PHOTO_LIBRARY, self._select_additional_photos, self.additional_status,
                ),
                self._section(
                    "Audio", "Attach an existing audio recording.",
                    "Choose audio", ft.Icons.AUDIO_FILE, self._select_audio, self.audio_status,
                ),
            ],
        )

    @staticmethod
    def _section(title: str, description: str, label: str, icon: str, on_click, status: ft.Text) -> ft.Control:
        return ft.Container(
            padding=14,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
            border_radius=12,
            content=ft.Column(
                tight=True,
                spacing=8,
                controls=[
                    ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=NAVY),
                    ft.Text(description, size=12, color=MUTED),
                    ft.OutlinedButton(content=label, icon=icon, on_click=on_click),
                    status,
                ],
            ),
        )

    def _refresh(self, control: ft.Text, files: list, empty_message: str) -> None:
        control.value = ", ".join(file.name for file in files) if files else empty_message
        self._page.update()

    async def _select_photo(self) -> None:
        files = await self._file_picker.pick_files(
            dialog_title="Select a photo",
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=False,
            with_data=True,
            compression_quality=75,
        )
        if files:
            self._photo_files[:] = files
            self._refresh(self.photo_status, files, "No photo selected")

    async def _select_additional_photos(self) -> None:
        files = await self._file_picker.pick_files(
            dialog_title="Select additional photos",
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=True,
            with_data=True,
            compression_quality=75,
        )
        if files:
            self._additional_photo_files.extend(files)
            self._refresh(self.additional_status, self._additional_photo_files, "No additional photos selected")

    async def _select_audio(self) -> None:
        files = await self._file_picker.pick_files(
            dialog_title="Select an audio recording",
            file_type=ft.FilePickerFileType.AUDIO,
            allow_multiple=False,
            with_data=True,
        )
        if files:
            self._audio_files[:] = files
            self._refresh(self.audio_status, files, "No audio selected")

    @staticmethod
    def _attachment(file) -> ReportAttachment:
        return ReportAttachment(filename=file.name, content=file.bytes or b"")

    @property
    def photo(self) -> ReportAttachment | None:
        return self._attachment(self._photo_files[0]) if self._photo_files else None

    @property
    def additional_photos(self) -> tuple[ReportAttachment, ...]:
        return tuple(self._attachment(file) for file in self._additional_photo_files)

    @property
    def audio(self) -> ReportAttachment | None:
        return self._attachment(self._audio_files[0]) if self._audio_files else None
