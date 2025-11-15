import reflex as rx
from app.states.menu_state import MenuState, MenuItem, MenuSection


def _allergen_badge(allergen: str) -> rx.Component:
    """A small badge to display an allergen."""
    return rx.el.span(
        allergen,
        class_name="bg-red-900 text-red-300 text-xs font-medium px-2.5 py-0.5 rounded-full",
    )


def _ingredient_tag(ingredient: str) -> rx.Component:
    """A tag for displaying an ingredient."""
    return rx.el.span(
        ingredient,
        class_name="bg-gray-700 text-gray-300 text-xs font-medium px-2 py-1 rounded-md",
    )


def _menu_item_card(item: MenuItem) -> rx.Component:
    """Card to display a single menu item."""
    return rx.el.div(
        rx.el.div(
            rx.el.p(item["name"], class_name="font-semibold text-lg text-gray-100"),
            rx.el.p(
                f"€{item['price']:.2f}", class_name="font-bold text-lg text-red-500"
            ),
            class_name="flex justify-between items-center mb-3",
        ),
        rx.cond(
            item["ingredients"].length() > 0,
            rx.el.div(
                rx.el.p(
                    "Ingredientes:", class_name="text-sm font-medium text-gray-400 mb-2"
                ),
                rx.el.div(
                    rx.foreach(item["ingredients"], _ingredient_tag),
                    class_name="flex flex-wrap gap-2 mb-4",
                ),
            ),
            None,
        ),
        rx.cond(
            item["allergens"].length() > 0,
            rx.el.div(
                rx.el.p(
                    "Alérgenos:", class_name="text-sm font-medium text-gray-400 mb-2"
                ),
                rx.el.div(
                    rx.foreach(item["allergens"], _allergen_badge),
                    class_name="flex flex-wrap gap-2",
                ),
            ),
            None,
        ),
        class_name="bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-700 hover:shadow-lg hover:border-red-500 transition-all duration-300 transform hover:-translate-y-1",
    )


def _menu_section(section: MenuSection) -> rx.Component:
    """Component to display a section of the menu."""
    return rx.el.div(
        rx.el.h2(
            section["title"],
            class_name="text-2xl font-bold text-gray-100 mb-6 border-b-2 border-red-600 pb-2",
        ),
        rx.el.div(
            rx.foreach(section["items"], _menu_item_card),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
        ),
        class_name="mb-12",
    )


def _menu_not_found() -> rx.Component:
    """Component to display when a menu is not found."""
    return rx.el.div(
        rx.el.div(
            rx.icon("search-x", class_name="h-16 w-16 text-red-500"),
            rx.el.h2(
                "Menu Not Found", class_name="text-2xl font-bold text-gray-100 mt-4"
            ),
            rx.el.p(
                "Sorry, we couldn't find the menu you're looking for.",
                class_name="text-gray-400 mt-2",
            ),
            rx.el.a(
                "View Sample Menu",
                href="/menu/sample",
                class_name="mt-6 inline-block bg-red-600 text-white font-medium py-2 px-4 rounded-lg shadow-md hover:bg-red-700 transition-colors",
            ),
            class_name="text-center bg-gray-800 p-12 rounded-lg shadow-lg border border-gray-700",
        ),
        class_name="flex items-center justify-center h-[60vh]",
    )


def menu_display() -> rx.Component:
    """The main component to display the entire menu."""
    return rx.el.div(
        rx.cond(
            MenuState.menu_found,
            rx.el.div(
                rx.foreach(MenuState.menu_data, _menu_section),
                class_name="w-full max-w-5xl mx-auto",
            ),
            _menu_not_found(),
        ),
        class_name="p-4 sm:p-8",
    )