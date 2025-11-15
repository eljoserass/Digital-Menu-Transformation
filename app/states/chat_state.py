import reflex as rx
from typing import TypedDict
import asyncio


class Message(TypedDict):
    role: str
    content: str


MOCK_RESPONSE = [
    "Of course! ",
    "The Coded Carbonara is one of our specials. ",
    "It features perfectly al dente pasta, ",
    "crispy bacon, a creamy sauce made with fresh eggs, ",
    "and a generous amount of sharp cheese. ",
    "It contains gluten, dairy, and eggs. ",
    "Would you like to know more about another dish?",
]
from app.states.menu_state import MenuState
from openai import OpenAI
from pathlib import Path


def menu_to_str(menu_id: str) -> str:
    menu_path = Path("menus") / f"{menu_id}.json"
    print("MENU PATH = ", menu_path)
    if menu_path.exists():
        with open(menu_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


class ChatState(rx.State):
    """Manages the state for the chat interface."""

    messages: list[Message] = []
    current_message: str = ""
    is_streaming: bool = False

    def _add_message(self, content: str, role: str):
        """Helper to add a new message to the list."""
        self.messages.append({"role": role, "content": content})

    @rx.event(background=True)
    async def stream_response(self):
        """Streams the mock response to the user."""
        async with self:
            menu_state = await self.get_state(MenuState)
            self.is_streaming = True
            self._add_message(f"", "assistant")
            client_openai = OpenAI()
            sys_prompt = f"\n            you are an expert sommelier, guide the user through the menu to recommend choices of drinks and food based on the vibe. \n            try to recommend damm products\n\n            answer briefly dont be so verbose, the context is that someone is at the bar or restaurant\n            they are almost on the move, talk as if you were standing there taking their order\n            messages should be short                 \n\n            dont sound ai generated           \n                                        \n            tis is the menu\n            ```json\n                \n            {menu_to_str(menu_state.menu_id)}\n            ```\n            "
            sys_prompt = f"you are a n expert sommelier, guide the user through the menu to recommend choices of drinks and food based on the vibe. try to recommend damm products\n\n                tis is the menu\n                ```json\n                {menu_to_str(menu_state.menu_id)}\n                ```\n            "
            input_list = [{"role": "system", "content": sys_prompt}] + self.messages
            stream = client_openai.responses.create(
                model="gpt-4.1-2025-04-14", input=input_list, stream=True
            )
        for event in stream:
            if event.__class__.__name__ == "ResponseTextDeltaEvent":
                async with self:
                    self.messages[-1]["content"] += event.delta
                yield
        async with self:
            self.is_streaming = False

    @rx.event
    def handle_send(self, form_data: dict[str, str]):
        """Handles sending a message from the user."""
        message = form_data.get("message", "").strip()
        if not message:
            return
        self._add_message(message, "user")
        self.current_message = ""
        return ChatState.stream_response