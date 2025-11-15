import reflex as rx


class ThemeState(rx.State):
    """Manages the theme of the application."""

    theme: str = "light"

    @rx.event
    def toggle_theme(self):
        """Toggles between light and dark themes."""
        self.theme = "dark" if self.theme == "light" else "light"