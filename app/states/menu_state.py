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
        "title": "Tapas",
        "items": [
            {
                "name": "Patatas Bravas",
                "price": 6.5,
                "ingredients": ["Patatas", "Salsa brava", "Aceite de oliva"],
                "allergens": [],
            },
            {
                "name": "Jamón Ibérico de Bellota",
                "price": 24.0,
                "ingredients": ["Jamón ibérico de bellota", "Picos de pan"],
                "allergens": ["Gluten"],
            },
            {
                "name": "Croquetas de Jamón",
                "price": 8.0,
                "ingredients": ["Jamón", "Bechamel", "Pan rallado"],
                "allergens": ["Gluten", "Lácteos"],
            },
            {
                "name": "Pan con Tomate",
                "price": 4.5,
                "ingredients": ["Pan de coca", "Tomate", "Aceite de oliva", "Sal"],
                "allergens": ["Gluten"],
            },
            {
                "name": "Aceitunas Aliñadas",
                "price": 3.5,
                "ingredients": ["Aceitunas verdes", "Ajo", "Tomillo", "Naranja"],
                "allergens": [],
            },
        ],
    },
    {
        "title": "Platos Principales",
        "items": [
            {
                "name": "Paella Valenciana",
                "price": 18.5,
                "ingredients": [
                    "Arroz bomba",
                    "Pollo",
                    "Conejo",
                    "Judía verde",
                    "Garrofó",
                    "Azafrán",
                ],
                "allergens": [],
            },
            {
                "name": "Pulpo a la Gallega",
                "price": 21.0,
                "ingredients": [
                    "Pulpo",
                    "Patatas",
                    "Pimentón de la Vera",
                    "Aceite de oliva virgen extra",
                ],
                "allergens": ["Moluscos"],
            },
            {
                "name": "Cordero Asado con Patatas a lo Pobre",
                "price": 25.0,
                "ingredients": [
                    "Paletilla de cordero",
                    "Patatas",
                    "Pimientos",
                    "Cebolla",
                ],
                "allergens": [],
            },
        ],
    },
    {
        "title": "Postres",
        "items": [
            {
                "name": "Tarta de Santiago",
                "price": 7.0,
                "ingredients": ["Almendras", "Azúcar", "Huevo", "Limón"],
                "allergens": ["Frutos de cáscara", "Huevo"],
            },
            {
                "name": "Crema Catalana",
                "price": 6.5,
                "ingredients": ["Leche", "Yema de huevo", "Azúcar", "Canela", "Limón"],
                "allergens": ["Lácteos", "Huevo"],
            },
            {
                "name": "Flan de Huevo Casero",
                "price": 5.5,
                "ingredients": ["Huevo", "Leche", "Azúcar", "Caramelo"],
                "allergens": ["Huevo", "Lácteos"],
            },
        ],
    },
    {
        "title": "Bebidas",
        "items": [
            {
                "name": "Estrella Damm",
                "price": 3.5,
                "ingredients": ["Agua", "Malta de cebada", "Arroz", "Lúpulo"],
                "allergens": ["Gluten"],
            },
            {
                "name": "Copa de Sangría",
                "price": 5.0,
                "ingredients": ["Vino tinto", "Frutas de temporada", "Azúcar", "Licor"],
                "allergens": ["Sulfitos"],
            },
            {
                "name": "Agua Mineral (50cl)",
                "price": 2.5,
                "ingredients": ["Agua mineral natural"],
                "allergens": [],
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
        """Load menu data from a JSON file based on the menu_id from the URL."""
        menu_id = self.router.page.params.get("menu_id", "")
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