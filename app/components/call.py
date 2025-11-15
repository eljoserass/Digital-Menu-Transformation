import reflex as rx
from app.states.call_state import CallState, CALL_UPLOAD_ID


def _record_button() -> rx.Component:
    """The button to start and stop recording."""
    return rx.el.div(
        rx.el.button(
            rx.cond(
                CallState.is_recording,
                rx.icon("radio", class_name="h-12 w-12 text-white animate-pulse"),
                rx.icon("mic", class_name="h-12 w-12 text-white"),
            ),
            on_click=rx.cond(
                CallState.is_recording,
                CallState.stop_recording,
                CallState.start_recording,
            ),
            class_name="flex items-center justify-center h-32 w-32 rounded-full bg-red-600 hover:bg-red-700 transition-all duration-300 shadow-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50",
        ),
        rx.el.p(
            rx.cond(CallState.is_recording, "Tap to stop", "Tap to speak"),
            class_name="text-center text-gray-500 mt-4",
        ),
        class_name="flex flex-col items-center",
    )


def _processing_view() -> rx.Component:
    """View displayed while the audio is being processed."""
    return rx.el.div(
        rx.spinner(class_name="h-16 w-16 text-red-600"),
        rx.el.p("Thinking...", class_name="text-lg font-medium text-gray-300 mt-4"),
        class_name="flex flex-col items-center justify-center p-8",
    )


def _response_view() -> rx.Component:
    """View to display the audio response from the assistant."""
    return rx.el.div(
        rx.el.h3("Here's my response:", class_name="text-xl font-bold text-gray-100"),
        rx.el.audio(
            src=CallState.audio_response_src,
            controls=True,
            autoplay=True,
            class_name="w-full mt-4",
        ),
        rx.el.button(
            rx.icon("refresh-ccw", class_name="mr-2 h-4 w-4"),
            "Ask Another Question",
            on_click=CallState.reset_state,
            class_name="flex items-center justify-center w-full mt-6 px-6 py-3 bg-gray-700 text-gray-200 font-semibold rounded-lg hover:bg-gray-600 transition-colors",
        ),
        class_name="w-full max-w-md p-8 bg-gray-800 rounded-xl shadow-lg border border-gray-700",
    )


def call_interface() -> rx.Component:
    """The main interface for the call tab."""
    return rx.el.div(
        rx.cond(
            CallState.audio_response_src != "",
            _response_view(),
            rx.cond(
                CallState.is_processing,
                _processing_view(),
                rx.el.div(
                    rx.el.h2(
                        "Voice Assistant",
                        class_name="text-3xl font-bold text-gray-100 mb-2",
                    ),
                    rx.el.p(
                        "Ask me anything about the menu!",
                        class_name="text-gray-400 mb-12",
                    ),
                    _record_button(),
                    rx.cond(
                        CallState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-5 w-5 mr-2"),
                            CallState.error_message,
                            class_name="flex items-center mt-6 text-sm text-red-500 bg-red-900 p-3 rounded-lg",
                        ),
                        None,
                    ),
                    class_name="text-center",
                ),
            ),
        ),
        class_name="flex items-center justify-center h-[calc(100vh-8.5rem)] w-full max-w-3xl mx-auto",
    )