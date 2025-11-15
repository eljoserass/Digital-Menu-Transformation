import reflex as rx
from app.components.menu import menu_display
from app.states.menu_state import MenuState, MenuPageState
from app.components.upload import upload_page
from app.components.chat import chat_interface
from app.components.call import call_interface
from app.states.theme_state import ThemeState


def index() -> rx.Component:
    """The index page, which redirects to the sample menu."""
    return rx.center(
        rx.el.p("Redirecting to sample menu..."), on_mount=rx.redirect("/menu/sample")
    )


def _tab_button(
    text: str, is_active: rx.Var[bool], on_click: rx.event.Event
) -> rx.Component:
    """A styled button for the tab navigation."""
    return rx.el.button(
        text,
        on_click=on_click,
        class_name=rx.cond(
            is_active,
            "px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-md",
            "px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700 rounded-md",
        ),
    )


def _theme_toggle() -> rx.Component:
    """A button to toggle between light and dark mode."""
    return rx.el.button(
        rx.cond(
            ThemeState.theme == "light",
            rx.icon("sun", class_name="h-5 w-5"),
            rx.icon("moon", class_name="h-5 w-5"),
        ),
        on_click=ThemeState.toggle_theme,
        class_name="p-2 rounded-full text-gray-500 hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-700",
    )


def menu_page() -> rx.Component:
    """The main page of the app, displaying the menu and chat tabs."""
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.div(class_name="w-10"),
                rx.el.div(
                    _tab_button(
                        "Menu",
                        MenuPageState.active_tab == "menu",
                        MenuPageState.set_active_tab("menu"),
                    ),
                    _tab_button(
                        "Chat",
                        MenuPageState.active_tab == "chat",
                        MenuPageState.set_active_tab("chat"),
                    ),
                    _tab_button(
                        "Call",
                        MenuPageState.active_tab == "call",
                        MenuPageState.set_active_tab("call"),
                    ),
                    class_name="flex items-center gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg mx-auto",
                ),
                rx.el.div(_theme_toggle(), class_name="w-10 flex justify-end"),
                class_name="flex items-center justify-between w-full max-w-5xl mx-auto",
            ),
            class_name="bg-white dark:bg-gray-900 shadow-md p-4 w-full border-b dark:border-gray-700",
        ),
        rx.match(
            MenuPageState.active_tab,
            ("menu", menu_display()),
            ("chat", chat_interface()),
            ("call", call_interface()),
            menu_display(),
        ),
        class_name="font-['Roboto'] bg-gray-50 dark:bg-black min-h-screen text-gray-700 dark:text-gray-300",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")
app.add_page(menu_page, route="/menu/[menu_id]", on_load=MenuState.load_menu)
app.add_page(upload_page, route="/upload")