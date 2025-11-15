import reflex as rx
from typing import TypedDict, Literal
import json
from pathlib import Path
import logging


class MenuItem(TypedDict):
    name: str
    price: float
    ingredients: list[str]
    allergens: list[str]


class MenuSection(TypedDict):
    title: str
    items: list[MenuItem]


SAMPLE_MENU_DATA = [
    {
        "title": "Appetizers",
        "items": [
            {
                "name": "Classic Bruschetta",
                "price": 8.99,
                "ingredients": [
                    "Toasted Bread",
                    "Tomatoes",
                    "Garlic",
                    "Basil",
                    "Olive Oil",
                ],
                "allergens": ["Gluten"],
            },
            {
                "name": "Spinach Artichoke Dip",
                "price": 10.5,
                "ingredients": [
                    "Spinach",
                    "Artichoke Hearts",
                    "Cream Cheese",
                    "Parmesan",
                ],
                "allergens": ["Dairy"],
            },
        ],
    },
    {
        "title": "Main Courses",
        "items": [
            {
                "name": "Grilled Salmon",
                "price": 22.0,
                "ingredients": ["Salmon Fillet", "Asparagus", "Lemon", "Herbs"],
                "allergens": [],
            },
            {
                "name": "Spaghetti Carbonara",
                "price": 16.0,
                "ingredients": ["Spaghetti", "Pancetta", "Egg Yolk", "Pecorino Cheese"],
                "allergens": ["Gluten", "Egg", "Dairy"],
            },
        ],
    },
]


class MenuState(rx.State):
    """Holds the state for the digital menu."""

    menu_data: list[MenuSection] = []
    menu_found: bool = True
    current_menu_id: str = ""

    @rx.event
    def load_menu(self):
        """Load menu data from a JSON file based on the menu_id in the URL."""
        menu_id = self.router.page.params.get("menu_id", "sample")
        self.current_menu_id = menu_id
        if menu_id == "sample":
            self.menu_data = SAMPLE_MENU_DATA
            self.menu_found = True
            return
        menu_path = Path("menus") / f"{menu_id}.json"
        try:
            with menu_path.open("r") as f:
                self.menu_data = json.load(f)
            self.menu_found = True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.exception(f"Could not load menu '{menu_id}': {e}")
            self.menu_found = False
            self.menu_data = []


class MenuPageState(rx.State):
    """Manages the state for the menu page (e.g., active tab)."""

    active_tab: Literal["menu", "chat", "call"] = "menu"

    @rx.event
    def set_active_tab(self, tab_name: str):
        """Sets the active tab."""
        self.active_tab = tab_name

    @rx.event
    def reset_tab(self):
        """Resets the active tab to 'menu' when the page loads."""
        self.active_tab = "menu"