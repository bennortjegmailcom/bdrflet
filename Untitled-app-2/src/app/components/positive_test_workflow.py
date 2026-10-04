"""Positive-test workflow; lockout eligibility is enforced by the service."""

import flet as ft

from app.components.action_buttons import primary_button
from app.models.job_card import JobCard
from app.models.lockout import LockoutState
from app.models.positive_test import PositiveTest
from app.models.report import ReportAttachment
from app.state import AppState
from app.theme import MUTED, NAVY
from app.services.permission_service import START_POSITIVE_TEST


_TEST_RESULTS = ("Pass", "Fail", "Inconclusive")


def build_positive_test_workflow(
    page: ft.Page, state: AppState, job: JobCard, router
) -> ft.Control:
    lockout = state.lockouts.get(job.job_card_id)
    active = lockout is not None and lockout.status == LockoutState.LOCKOUT_ACTIVE
    permitted = state.permission_service.has_permission(
        state.current_user, START_POSITIVE_TEST
    )
    async def submit_test(
        result_value: str, notes: str, photo_files: list, form_error: ft.Text
    ) -> None:
        photos = tuple(
            ReportAttachment(filename=item.name, content=item.bytes or b"")
            for item in photo_files
        )
        try:
            await state.positive_test_service.start(
                job.job_card_id,
                state.current_user,
                result_value,
                notes,
                photos,
            )
        except (ValueError, PermissionError) as exc:
            form_error.value = str(exc)
            page.update()
            return
        except Exception:
            form_error.value = "Could not record the positive test. Please try again."
            page.update()
            return
        state.positive_tests[job.job_card_id] = await state.positive_test_service.get_for_job_card(
            job.job_card_id
        )
        page.pop_dialog()
        router.go("/job-card-detail")

    def show_test_form() -> None:
        result_field = ft.Dropdown(
            label="Test result",
            hint_text="Select a result",
            options=[ft.DropdownOption(key=item, text=item) for item in _TEST_RESULTS],
        )
        notes_field = ft.TextField(
            label="Notes",
            hint_text="Record observations",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        photo_status = ft.Text("No test photos selected", size=12, color=MUTED)
        photo_files: list = []
        form_error = ft.Text("", size=12, color=ft.Colors.RED_700)

        async def choose_photos() -> None:
            selected = await router.file_picker.pick_files(
                dialog_title="Select test photos",
                file_type=ft.FilePickerFileType.IMAGE,
                allow_multiple=True,
                with_data=True,
                compression_quality=75,
            )
            if selected:
                photo_files.extend(selected)
                photo_status.value = ", ".join(item.name for item in photo_files)
                page.update()

        async def save() -> None:
            if not result_field.value:
                result_field.error_text = "Test result is required."
                page.update()
                return
            await submit_test(
                result_field.value,
                notes_field.value or "",
                photo_files,
                form_error,
            )

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Start positive test", color=NAVY, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text(f"Job card: {job.job_card_id}", color=NAVY),
                        ft.Text(f"Equipment: {job.equipment} · {job.equipment_id}", color=NAVY),
                        ft.Text(f"Lockout: {lockout.lockout_id if lockout else '—'}", color=NAVY),
                        result_field,
                        notes_field,
                        ft.OutlinedButton(
                            content="Add photos",
                            icon=ft.Icons.ADD_A_PHOTO,
                            on_click=choose_photos,
                        ),
                        photo_status,
                        form_error,
                        ft.Text(
                            "This records the authorised user's test entry; it does not change lockout state.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(content="Cancel", on_click=page.pop_dialog),
                    ft.Button(content="Save positive test", on_click=save),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    start_button = primary_button("START POSITIVE TEST", show_test_form)
    start_button.disabled = not (active and permitted)
    controls: list[ft.Control] = [
        ft.Text("POSITIVE TEST", size=16, weight=ft.FontWeight.BOLD, color=NAVY),
    ]

    if not active:
        controls.extend([
            ft.Text("LOCKOUT REQUIRED", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900),
            ft.Text(
                "This positive test cannot proceed until the required lockout workflow has been completed.",
                size=13,
                color=NAVY,
            ),
        ])
    else:
        controls.extend([
            ft.Text("✓ Equipment confirmed", size=13, color=ft.Colors.GREEN_800),
            ft.Text("✓ SCADA stop confirmed", size=13, color=ft.Colors.GREEN_800),
            ft.Text("✓ Physical lockout confirmed", size=13, color=ft.Colors.GREEN_800),
        ])
        if not permitted:
            controls.append(ft.Text("Your role is not authorised to start this test.", size=12, color=MUTED))

    controls.append(start_button)
    records = state.positive_tests.get(job.job_card_id, ())
    controls.append(ft.Text("Positive test records", size=14, weight=ft.FontWeight.W_600, color=NAVY))
    if records:
        controls.extend(_test_record_control(record) for record in records)
    else:
        controls.append(ft.Text("No positive tests recorded.", size=12, color=MUTED))

    return ft.Container(
        padding=14,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(tight=True, spacing=9, controls=controls),
    )


def _test_record_control(record: PositiveTest) -> ft.Control:
    details = [
        ft.Text(f"{record.positive_test_id} · {record.result}", size=13, weight=ft.FontWeight.W_600, color=NAVY),
        ft.Text(f"{record.user_name} · {record.timestamp}", size=12, color=MUTED),
        ft.Text(f"{record.equipment} · {record.equipment_id} · {record.lockout_id}", size=12, color=NAVY),
    ]
    if record.notes:
        details.append(ft.Text(record.notes, size=12, color=NAVY))
    if record.photos:
        details.append(ft.Text("Photos: " + ", ".join(photo.filename for photo in record.photos), size=12, color=MUTED))
    return ft.Container(
        padding=10,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        content=ft.Column(tight=True, spacing=4, controls=details),
    )
