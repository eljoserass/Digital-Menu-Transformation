import reflex as rx
from typing import TypedDict
import asyncio
from app.states.menu_state import MenuState
from openai import OpenAI
from pathlib import Path
import logging


class Message(TypedDict):
    role: str
    content: str


def menu_to_str(menu_id: str) -> str:
    """Reads menu data from a JSON file."""
    if not menu_id:
        return "{}"
    menu_path = Path("menus") / f"{menu_id}.json"
    logging.info(f"Loading menu from path: {menu_path}")
    if menu_path.exists():
        try:
            with open(menu_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.exception(f"Failed to read menu file {menu_path}: {e}")
            return "{}"
    logging.warning(f"Menu file not found at {menu_path}")
    return "{}"


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
            menu_json_str = menu_to_str(menu_state.current_menu_id)
            self.is_streaming = True
            self._add_message("", "assistant")
            client_openai = OpenAI()
            sys_prompt = f"\n            You are an expert sommelier and waiter. Your goal is to guide the user through the menu,\n            recommending food and drinks, especially Damm products if available.\n            Your tone should be brief, friendly, and conversational, like you're speaking to someone at a bar or restaurant.\n            Keep your messages short and to the point. Avoid sounding like an AI.\n\n            This is the menu you are working with:\n            \n            {menu_json_str}\n            \n            "
            messages_for_api = [
                {"role": "system", "content": sys_prompt}
            ] + self.messages
        try:
            stream = client_openai.chat.completions.create(
                model="gpt-4-turbo", messages=messages_for_api, stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    async with self:
                        self.messages[-1]["content"] += delta
                    yield
        except Exception as e:
            logging.exception(f"OpenAI stream failed: {e}")
            async with self:
                self.messages[-1]["content"] = (
                    "Sorry, I'm having trouble connecting right now."
                )
        finally:
            async with self:
                self.is_streaming = False

    @rx.event
    def handle_send(self, form_data: dict[str, str]):
        """Handles sending a message from the user."""
        message = form_data.get("message", "").strip()
        if not message or self.is_streaming:
            return
        self._add_message(message, "user")
        self.current_message = ""
        return ChatState.stream_response