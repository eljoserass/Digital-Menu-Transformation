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
            self._add_message(
                f"(Querying menu: {menu_state.current_menu_id})\n\n", "assistant"
            )
        for chunk in MOCK_RESPONSE:
            await asyncio.sleep(0.1)
            async with self:
                self.messages[-1]["content"] += chunk
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