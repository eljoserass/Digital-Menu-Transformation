import reflex as rx
from app.states.chat_state import ChatState, Message


def _message_bubble(message: Message) -> rx.Component:
    """A message bubble component."""
    is_user = message["role"] == "user"
    return rx.el.div(
        rx.el.div(
            rx.markdown(message["content"], class_name="text-sm"),
            class_name=rx.cond(
                is_user,
                "bg-red-600 text-white p-3 rounded-l-lg rounded-t-lg",
                "bg-gray-200 text-gray-800 p-3 rounded-r-lg rounded-t-lg",
            ),
            max_width="80%",
        ),
        class_name=rx.cond(
            is_user, "flex justify-end w-full", "flex justify-start w-full"
        ),
    )


def chat_interface() -> rx.Component:
    """The main chat interface component."""
    return rx.el.div(
        rx.el.div(
            rx.foreach(ChatState.messages, _message_bubble),
            class_name="flex-1 p-4 space-y-4 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        name="message",
                        placeholder="Ask about the menu...",
                        class_name="flex-1 px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-red-500",
                        disabled=ChatState.is_streaming,
                        default_value=ChatState.current_message,
                    ),
                    rx.el.button(
                        rx.icon("send", class_name="h-5 w-5"),
                        type_="submit",
                        class_name="px-4 py-2 bg-red-600 text-white rounded-r-lg hover:bg-red-700 disabled:bg-gray-400",
                        disabled=ChatState.is_streaming,
                    ),
                    class_name="flex",
                ),
                on_submit=ChatState.handle_send,
                reset_on_submit=True,
                width="100%",
            ),
            class_name="p-4 bg-white border-t",
        ),
        class_name="flex flex-col h-[80vh] w-full max-w-3xl mx-auto bg-white rounded-lg shadow-lg border border-gray-200 mt-8",
    )