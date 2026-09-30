from datetime import date

from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class ReminderCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(12)
        self.bind(pos=self._redraw, size=self._redraw)

        with self.canvas.before:
            Color(0.09, 0.30, 0.27, 1)
            self._shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])

    def _redraw(self, *_args):
        self._shape.pos = self.pos
        self._shape.size = self.size


class ReminderApp(App):
    title = "Daymark"

    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(36), dp(24), dp(24)],
            spacing=dp(20),
        )
        with root.canvas.before:
            Color(0.96, 0.97, 0.95, 1)
            self._background = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        root.bind(
            pos=lambda widget, _value: setattr(self._background, "pos", widget.pos),
            size=lambda widget, _value: setattr(self._background, "size", widget.size),
        )

        heading = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(82))
        heading.add_widget(
            Label(
                text="Your day, at a glance",
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(26),
                bold=True,
                halign="left",
                valign="middle",
            )
        )
        heading.add_widget(
            Label(
                text=date.today().strftime("%A, %B %d"),
                color=(0.36, 0.41, 0.39, 1),
                font_size=dp(15),
                halign="left",
                valign="top",
            )
        )
        root.add_widget(heading)

        next_reminder = ReminderCard(size_hint_y=None, height=dp(190))
        next_reminder.add_widget(
            Label(
                text="NEXT REMINDER",
                color=(0.72, 0.86, 0.78, 1),
                font_size=dp(12),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(22),
            )
        )
        next_reminder.add_widget(
            Label(
                text="Nothing scheduled yet",
                color=(1, 1, 1, 1),
                font_size=dp(22),
                bold=True,
                halign="left",
            )
        )
        next_reminder.add_widget(
            Label(
                text="Your next reminder will appear here.",
                color=(0.84, 0.90, 0.86, 1),
                font_size=dp(15),
                halign="left",
            )
        )
        root.add_widget(next_reminder)

        root.add_widget(
            Label(
                text="Today's reminders",
                color=(0.12, 0.17, 0.16, 1),
                font_size=dp(20),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(32),
            )
        )
        root.add_widget(
            Label(
                text="A clear day starts here.",
                color=(0.36, 0.41, 0.39, 1),
                font_size=dp(15),
                halign="left",
            )
        )
        return root


if __name__ == "__main__":
    ReminderApp().run()