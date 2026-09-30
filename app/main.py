import logging
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

from kivy.app import App
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from app.database.database import Database
from app.database.repositories.reminder_repository import ReminderRepository
from app.models.reminder import Reminder
from app.services.reminder_service import ReminderService
from app.utils.reminder_input import parse_due_date, parse_local_time, parse_weekdays


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeftLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)
        self._update_text_size()

    def _update_text_size(self, *_args):
        self.text_size = self.size


class ReminderCard(BoxLayout):
    def __init__(self, **kwargs):
        self.orientation = kwargs.pop("orientation", "vertical")
        super().__init__(**kwargs)
        self.padding = dp(20)
        self.spacing = dp(12)
        self.bind(pos=self._redraw, size=self._redraw)

        with self.canvas.before:
            Color(0.09, 0.30, 0.27, 1)
            self._shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])

    def _redraw(self, *_args):
        self._shape.pos = self.pos
        self._shape.size = self.size


class HomeScreen(BoxLayout):
    def __init__(self, service: ReminderService, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.orientation = "vertical"
        self.padding = [dp(20), dp(24), dp(20), dp(20)]
        self.spacing = dp(14)

        with self.canvas.before:
            Color(0.96, 0.97, 0.95, 1)
            self._background = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda widget, _value: setattr(self._background, "pos", widget.pos),
            size=lambda widget, _value: setattr(self._background, "size", widget.size),
        )

        heading = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(66))
        heading.add_widget(
            LeftLabel(
                text="Daymark",
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(27),
                bold=True,
            )
        )
        heading.add_widget(
            LeftLabel(
                text=date.today().strftime("%A, %B %d"),
                color=(0.36, 0.41, 0.39, 1),
                font_size=dp(14),
            )
        )
        self.add_widget(heading)

        self.next_card = ReminderCard(size_hint_y=None, height=dp(148))
        self.next_title = LeftLabel(
            text="Nothing scheduled yet",
            color=(1, 1, 1, 1),
            font_size=dp(21),
            bold=True,
            size_hint_y=None,
            height=dp(36),
        )
        self.next_detail = LeftLabel(
            text="Your next reminder will appear here.",
            color=(0.84, 0.90, 0.86, 1),
            font_size=dp(14),
        )
        self.next_card.add_widget(
            LeftLabel(
                text="NEXT REMINDER",
                color=(0.72, 0.86, 0.78, 1),
                font_size=dp(12),
                bold=True,
                size_hint_y=None,
                height=dp(20),
            )
        )
        self.next_card.add_widget(self.next_title)
        self.next_card.add_widget(self.next_detail)
        self.add_widget(self.next_card)

        self.add_widget(
            LeftLabel(
                text="Today's reminders",
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(19),
                bold=True,
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.reminder_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.reminder_list.bind(minimum_height=self.reminder_list.setter("height"))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        scroll.add_widget(self.reminder_list)
        self.add_widget(scroll)

        add_button = Button(
            text="+  Add reminder",
            size_hint_y=None,
            height=dp(52),
            font_size=dp(16),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=(0.09, 0.30, 0.27, 1),
        )
        add_button.bind(on_release=lambda *_args: self.open_editor())
        self.add_widget(add_button)
        self.refresh()

    def refresh(self):
        reminders = self.service.list_reminders()
        now = datetime.now()
        upcoming = [
            (reminder, occurrence)
            for reminder in reminders
            if reminder.enabled
            if (occurrence := reminder.next_occurrence(now)) is not None
        ]
        upcoming.sort(key=lambda item: item[1])

        if upcoming:
            next_reminder, occurrence = upcoming[0]
            self.next_title.text = next_reminder.title
            self.next_detail.text = occurrence.strftime("%A, %I:%M %p")
        else:
            self.next_title.text = "Nothing scheduled yet"
            self.next_detail.text = "Add a reminder to see what's next."

        self.reminder_list.clear_widgets()
        if not reminders:
            self.reminder_list.add_widget(
                LeftLabel(
                    text="A clear day starts here.",
                    color=(0.36, 0.41, 0.39, 1),
                    font_size=dp(15),
                    size_hint_y=None,
                    height=dp(52),
                )
            )
            return

        reminders.sort(
            key=lambda reminder: (
                reminder.next_occurrence(now) or datetime.max,
                reminder.id or 0,
            )
        )
        for reminder in reminders:
            self.reminder_list.add_widget(self._build_reminder_row(reminder, now))

    def _build_reminder_row(self, reminder: Reminder, now: datetime) -> BoxLayout:
        row = ReminderCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(96),
            padding=dp(12),
            spacing=dp(8),
        )
        row.canvas.before.clear()
        with row.canvas.before:
            Color(1, 1, 1, 1)
            row._shape = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(12)])
        row.bind(pos=row._redraw, size=row._redraw)

        details = BoxLayout(orientation="vertical", spacing=dp(1))
        details.add_widget(
            LeftLabel(
                text=reminder.title,
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(16),
                bold=True,
            )
        )
        occurrence = reminder.next_occurrence(now) if reminder.enabled else None
        if not reminder.enabled:
            schedule_text = "Paused"
        elif occurrence is None:
            schedule_text = "Date has passed"
        else:
            schedule_text = occurrence.strftime("%a, %b %d at %I:%M %p")
        details.add_widget(
            LeftLabel(
                text=schedule_text,
                color=(0.36, 0.41, 0.39, 1),
                font_size=dp(13),
            )
        )
        row.add_widget(details)
        row.add_widget(
            self._row_button(
                "Edit",
                lambda *_args: self.open_editor(reminder),
                (0.90, 0.93, 0.90, 1),
            )
        )
        row.add_widget(
            self._row_button(
                "On" if reminder.enabled else "Off",
                lambda *_args: self.toggle_reminder(reminder),
                (0.86, 0.92, 0.87, 1),
            )
        )
        row.add_widget(
            self._row_button(
                "Delete",
                lambda *_args: self.confirm_delete(reminder),
                (0.96, 0.88, 0.85, 1),
            )
        )
        return row

    @staticmethod
    def _row_button(text: str, action, background_color: tuple) -> Button:
        button = Button(
            text=text,
            size_hint_x=None,
            width=dp(58),
            font_size=dp(11),
            color=(0.12, 0.17, 0.16, 1),
            background_normal="",
            background_color=background_color,
        )
        button.bind(on_release=action)
        return button

    def toggle_reminder(self, reminder: Reminder):
        try:
            self.service.set_enabled(reminder.id, not reminder.enabled)
        except Exception:
            logger.exception("Could not change reminder enabled state")
        self.refresh()

    def confirm_delete(self, reminder: Reminder):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))
        content.add_widget(
            LeftLabel(text=f"Delete '{reminder.title}'?", color=(0.12, 0.17, 0.16, 1))
        )
        actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        popup = Popup(title="", content=content, size_hint=(0.88, None), height=dp(190))
        cancel = Button(text="Cancel")
        cancel.bind(on_release=popup.dismiss)
        delete = Button(text="Delete", color=(0.55, 0.12, 0.10, 1))
        delete.bind(on_release=lambda *_args: self._delete(reminder, popup))
        actions.add_widget(cancel)
        actions.add_widget(delete)
        content.add_widget(actions)
        popup.open()

    def _delete(self, reminder: Reminder, popup: Popup):
        try:
            self.service.delete(reminder.id)
            popup.dismiss()
            self.refresh()
        except Exception:
            logger.exception("Could not delete reminder")

    def open_editor(self, reminder: Reminder | None = None):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(38))
        header.add_widget(
            LeftLabel(
                text="Edit reminder" if reminder else "New reminder",
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(20),
                bold=True,
            )
        )
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.94, 0.90),
            auto_dismiss=True,
        )
        close_button = Button(text="X", size_hint_x=None, width=dp(42))
        close_button.bind(on_release=popup.dismiss)
        header.add_widget(close_button)
        content.add_widget(header)

        title_input = self._add_field(content, "Reminder", "What should you remember?", reminder.title if reminder else "")
        time_input = self._add_field(
            content,
            "Time",
            "24-hour time, for example 20:30",
            reminder.time.isoformat(timespec="minutes") if reminder else "",
        )

        is_recurring = reminder.repeats if reminder else False
        once_button = ToggleButton(
            text="One time", group="schedule-mode", state="normal" if is_recurring else "down"
        )
        repeat_button = ToggleButton(
            text="Repeat", group="schedule-mode", state="down" if is_recurring else "normal"
        )
        mode_controls = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        mode_controls.add_widget(once_button)
        mode_controls.add_widget(repeat_button)
        content.add_widget(mode_controls)

        schedule_label = LeftLabel(
            text="Days of the week" if is_recurring else "Date",
            color=(0.12, 0.17, 0.16, 1),
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20),
        )
        content.add_widget(schedule_label)
        if is_recurring:
            schedule_value = ", ".join(
                day_name
                for day_number, day_name in enumerate(
                    ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
                )
                if day_number in reminder.days
            )
        else:
            schedule_value = reminder.due_date.isoformat() if reminder else date.today().isoformat()
        schedule_input = TextInput(
            text=schedule_value,
            hint_text="Mon, Wed, Fri" if is_recurring else "YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            font_size=dp(15),
            padding=[dp(12), dp(10)],
        )
        content.add_widget(schedule_input)

        def set_mode(repeats: bool):
            schedule_label.text = "Days of the week" if repeats else "Date"
            schedule_input.hint_text = "Mon, Wed, Fri" if repeats else "YYYY-MM-DD"
            if (repeats != is_recurring) or reminder is None:
                schedule_input.text = ""

        once_button.bind(on_release=lambda *_args: set_mode(False))
        repeat_button.bind(on_release=lambda *_args: set_mode(True))

        notes_input = self._add_field(content, "Notes (optional)", "", reminder.notes if reminder else "")
        category_input = self._add_field(
            content,
            "Category (optional)",
            "For example: Health",
            reminder.category or "" if reminder else "",
        )
        error_label = LeftLabel(
            text="",
            color=(0.62, 0.16, 0.12, 1),
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30),
        )
        content.add_widget(error_label)
        save_button = Button(
            text="Save reminder",
            size_hint_y=None,
            height=dp(48),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=(0.09, 0.30, 0.27, 1),
        )
        save_button.bind(
            on_release=lambda *_args: self._save_reminder(
                popup,
                error_label,
                reminder,
                title_input,
                time_input,
                schedule_input,
                notes_input,
                category_input,
                repeat_button,
            )
        )
        content.add_widget(save_button)
        popup.open()

    @staticmethod
    def _add_field(parent: BoxLayout, label: str, hint: str, value: str) -> TextInput:
        field = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(2),
        )
        field.add_widget(
            LeftLabel(
                text=label,
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(13),
                size_hint_y=None,
                height=dp(20),
            )
        )
        text_input = TextInput(
            text=value,
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            font_size=dp(15),
            padding=[dp(12), dp(10)],
        )
        field.add_widget(text_input)
        parent.add_widget(field)
        return text_input

    def _save_reminder(
        self,
        popup: Popup,
        error_label: Label,
        existing: Reminder | None,
        title_input: TextInput,
        time_input: TextInput,
        schedule_input: TextInput,
        notes_input: TextInput,
        category_input: TextInput,
        repeat_button: ToggleButton,
    ):
        try:
            title = title_input.text.strip()
            if not title:
                raise ValueError("Enter a reminder name.")
            scheduled_time = parse_local_time(time_input.text)
            if repeat_button.state == "down":
                days = parse_weekdays(schedule_input.text)
                due_date = None
            else:
                days = ()
                due_date = parse_due_date(schedule_input.text)
            notes = notes_input.text.strip()
            category = category_input.text.strip() or None

            if existing is None:
                if due_date is not None:
                    self.service.create_one_time(
                        title, scheduled_time, due_date, notes=notes, category=category
                    )
                else:
                    self.service.create_recurring(
                        title, scheduled_time, days, notes=notes, category=category
                    )
            else:
                updated = replace(
                    existing,
                    title=title,
                    time=scheduled_time,
                    due_date=due_date,
                    days=days,
                    notes=notes,
                    category=category,
                )
                self.service.update(updated)

            popup.dismiss()
            self.refresh()
        except ValueError as error:
            error_label.text = str(error)
        except Exception:
            logger.exception("Could not save reminder")
            error_label.text = "Could not save this reminder. Please try again."


class ReminderApp(App):
    title = "Daymark"

    def build(self):
        database = Database(Path(self.user_data_dir) / "daymark.sqlite3")
        database.initialize()
        repository = ReminderRepository(database)
        return HomeScreen(ReminderService(repository))


if __name__ == "__main__":
    ReminderApp().run()