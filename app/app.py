import reflex as rx
from app.components.menu import menu_display
from app.states.menu_state import MenuState, MenuPageState
from app.components.upload import upload_page
from app.components.chat import chat_interface
from app.components.call import call_interface


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
            "px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-200 rounded-md",
        ),
    )


def menu_page() -> rx.Component:
    """The main page of the app, displaying the menu and chat tabs."""
    return rx.el.main(
        rx.el.header(
            rx.el.div(
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
                    class_name="flex items-center gap-2 p-1 bg-gray-100 rounded-lg mx-auto",
                ),
                class_name="flex items-center justify-center w-full max-w-5xl mx-auto",
            ),
            class_name="bg-white shadow-md p-4 w-full border-b",
        ),
        rx.match(
            MenuPageState.active_tab,
            ("menu", menu_display()),
            ("chat", chat_interface()),
            ("call", call_interface()),
            menu_display(),
        ),
        class_name="font-['Roboto'] bg-gray-50 min-h-screen text-gray-700",
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