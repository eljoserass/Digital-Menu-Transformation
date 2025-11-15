import reflex as rx
from app.states.call_state import CallState, CALL_UPLOAD_ID


def _record_button() -> rx.Component:
    """The button to start and stop recording."""
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("mic", class_name="h-12 w-12 text-white"),
                class_name="flex items-center justify-center h-32 w-32 rounded-full bg-blue-600 hover:bg-blue-700 transition-all duration-300 shadow-lg cursor-pointer",
            ),
            id=CALL_UPLOAD_ID,
            accept={"audio/webm": [".webm"], "audio/mp4": [".mp4"]},
            max_files=1,
            on_drop=CallState.handle_audio_upload(
                rx.upload_files(upload_id=CALL_UPLOAD_ID)
            ),
            class_name="flex justify-center",
        ),
        rx.el.p("Tap to speak", class_name="text-center text-gray-500 mt-4"),
    )


def _processing_view() -> rx.Component:
    """View displayed while the audio is being processed."""
    return rx.el.div(
        rx.spinner(class_name="h-16 w-16 text-blue-600"),
        rx.el.p("Thinking...", class_name="text-lg font-medium text-gray-700 mt-4"),
        class_name="flex flex-col items-center justify-center p-8",
    )


def _response_view() -> rx.Component:
    """View to display the audio response from the assistant."""
    return rx.el.div(
        rx.el.h3("Here's my response:", class_name="text-xl font-bold text-gray-800"),
        rx.el.audio(
            src=rx.get_upload_url(CallState.audio_response_src),
            controls=True,
            autoplay=True,
            class_name="w-full mt-4",
        ),
        rx.el.button(
            rx.icon("refresh-ccw", class_name="mr-2 h-4 w-4"),
            "Ask Another Question",
            on_click=CallState.reset_state,
            class_name="flex items-center justify-center w-full mt-6 px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors",
        ),
        class_name="w-full max-w-md p-8 bg-white rounded-xl shadow-lg border",
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
                        class_name="text-3xl font-bold text-gray-800 mb-2",
                    ),
                    rx.el.p(
                        "Ask me anything about the menu!",
                        class_name="text-gray-500 mb-12",
                    ),
                    _record_button(),
                    rx.cond(
                        CallState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-5 w-5 mr-2"),
                            CallState.error_message,
                            class_name="flex items-center mt-6 text-sm text-red-600 bg-red-100 p-3 rounded-lg",
                        ),
                        None,
                    ),
                    class_name="text-center",
                ),
            ),
        ),
        class_name="flex items-center justify-center h-[80vh] w-full max-w-3xl mx-auto mt-8",
    )