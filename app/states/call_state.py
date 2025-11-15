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

    async def _generate_audio_response(self) -> str:
        """Generates a mock audio response by returning a static file."""
        return "/sample.mp3"

    @rx.event
    def start_recording(self):
        """Starts the recording state."""
        self.is_recording = True

    @rx.event
    async def stop_recording(self):
        """Stops recording, processes, and gets response."""
        self.is_recording = False
        self.is_processing = True
        self.error_message = ""
        self.audio_response_src = ""
        yield
        try:
            await asyncio.sleep(1)
            response_filename = await self._generate_audio_response()
            if response_filename:
                self.audio_response_src = response_filename
        except Exception as e:
            logging.exception(f"Audio processing failed: {e}")
            self.error_message = "An unexpected error occurred."
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