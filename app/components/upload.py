import reflex as rx
from app.states.upload_state import UploadState, UPLOAD_ID


def _selected_file_view(file: str) -> rx.Component:
    """Component to display a single selected file."""
    return rx.el.div(
        rx.icon("file-image", class_name="h-5 w-5 text-gray-500"),
        rx.el.p(file, class_name="text-sm text-gray-700 truncate"),
        class_name="flex items-center gap-2 p-2 bg-gray-100 border border-gray-200 rounded-lg w-full",
    )


def _upload_button() -> rx.Component:
    """The button to trigger the upload and processing."""
    is_working = UploadState.uploading | UploadState.processing
    button_text = rx.cond(
        UploadState.uploading,
        "Uploading...",
        rx.cond(UploadState.processing, "Processing...", "Generate Menu"),
    )
    return rx.el.button(
        rx.cond(is_working, rx.spinner(class_name="h-4 w-4 mr-2"), None),
        button_text,
        on_click=UploadState.handle_upload(rx.upload_files(upload_id=UPLOAD_ID)),
        disabled=is_working,
        class_name="flex items-center justify-center w-full mt-4 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed",
    )


def _qr_code_display() -> rx.Component:
    """Displays the generated QR code."""
    return rx.el.div(
        rx.el.h3(
            "Your menu is ready!",
            class_name="text-xl font-bold text-center text-gray-800",
        ),
        rx.el.p(
            "Scan the QR code to view your menu.",
            class_name="text-center text-gray-500 mt-2 mb-4",
        ),
        rx.image(
            src=rx.get_upload_url(UploadState.qr_code_src),
            alt="Menu QR Code",
            width=200,
            height=200,
            class_name="mx-auto border-4 border-white rounded-lg shadow-lg",
        ),
        rx.el.input(
            default_value=UploadState.menu_url,
            read_only=True,
            class_name="w-full mt-4 p-2 text-center bg-gray-100 border rounded-md text-sm",
        ),
        rx.el.a(
            "Open Menu",
            href=UploadState.menu_url,
            is_external=True,
            class_name="mt-4 inline-block w-full text-center bg-blue-600 text-white font-medium py-2 px-4 rounded-lg shadow-md hover:bg-blue-700 transition-colors",
        ),
        rx.el.button(
            "Create Another Menu",
            on_click=UploadState.reset_state,
            class_name="mt-2 w-full text-center bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors",
        ),
        class_name="bg-white p-8 rounded-xl shadow-lg border border-gray-200 w-full max-w-sm",
    )


def upload_page() -> rx.Component:
    """The UI for the menu upload page."""
    return rx.el.div(
        rx.cond(
            UploadState.qr_code_src != "",
            _qr_code_display(),
            rx.el.div(
                rx.el.h2(
                    "Upload Your Menu", class_name="text-2xl font-bold text-gray-800"
                ),
                rx.el.p(
                    "Upload an image of your menu, and we'll digitize it for you.",
                    class_name="text-gray-500 mt-1",
                ),
                rx.upload.root(
                    rx.el.div(
                        rx.icon(
                            "cloud-upload", class_name="w-12 h-12 stroke-gray-400 mb-4"
                        ),
                        rx.el.p(
                            rx.el.strong("Click to upload", class_name="text-blue-600"),
                            " or drag and drop",
                            class_name="text-gray-600",
                        ),
                        rx.el.p(
                            "PNG, JPG, or JPEG up to 10MB",
                            class_name="text-xs text-gray-500",
                        ),
                        class_name="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 text-center",
                    ),
                    id=UPLOAD_ID,
                    accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                    max_files=1,
                    max_size=10000000,
                    multiple=False,
                    class_name="w-full mt-6 cursor-pointer",
                ),
                rx.el.div(
                    rx.foreach(rx.selected_files(UPLOAD_ID), _selected_file_view),
                    class_name="mt-4 space-y-2",
                ),
                rx.cond(
                    UploadState.error_message != "",
                    rx.el.div(
                        rx.icon("badge_alert", class_name="h-5 w-5 mr-2"),
                        UploadState.error_message,
                        class_name="flex items-center mt-4 text-sm text-red-600 bg-red-100 p-3 rounded-lg",
                    ),
                    None,
                ),
                _upload_button(),
                rx.el.a(
                    "< Back to Menu",
                    href="/menu/sample",
                    class_name="mt-6 text-sm text-blue-600 hover:underline text-center block",
                ),
                class_name="bg-white p-8 rounded-xl shadow-lg border border-gray-200 w-full max-w-lg",
            ),
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-50 p-4",
    )