import reflex as rx
import asyncio
import os
from pathlib import Path
import logging
import uuid
from app.states.menu_state import MenuState

CALL_UPLOAD_ID = "audio_upload"


class CallState(rx.State):
    """State for the voice call interface."""

    is_recording: bool = False
    is_processing: bool = False
    error_message: str = ""
    audio_response_src: str = ""
    uploaded_audio_path: str = ""

    async def _generate_audio_response(self) -> str:
        """Generates a mock audio response by returning a static file."""
        return "/sample.mp3"

    @rx.event
    def start_recording(self):
        """Starts the recording state and triggers JS recording."""
        self.is_recording = True
        return rx.call_script("startAudioRecording()")

    @rx.event
    def stop_recording(self):
        """Stops the recording state and triggers JS to stop and upload."""
        self.is_recording = False
        self.is_processing = True
        self.error_message = ""
        self.audio_response_src = ""
        return rx.call_script("stopAudioRecording()")

    @rx.event
    async def handle_audio_upload(self, files: list[rx.UploadFile]):
        """Handles the uploaded audio file from the frontend."""
        if not files:
            self.error_message = "Audio recording failed. Please try again."
            self.is_processing = False
            return
        try:
            uploaded_file = files[0]
            upload_data = await uploaded_file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            file_path = upload_dir / unique_filename
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.uploaded_audio_path = str(file_path)
            await asyncio.sleep(1)
            response_filename = await self._generate_audio_response()
            if response_filename:
                self.audio_response_src = response_filename
        except Exception as e:
            logging.exception(f"Audio processing failed: {e}")
            self.error_message = "An unexpected error occurred during processing."
        finally:
            self.is_processing = False
            yield

    @rx.event
    def reset_state(self):
        """Resets the call page to its initial state."""
        self.is_recording = False
        self.is_processing = False
        self.error_message = ""
        self.audio_response_src = ""