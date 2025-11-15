import reflex as rx
import asyncio
import os
from pathlib import Path
import logging
import uuid
from elevenlabs.client import ElevenLabs
from app.states.menu_state import MenuState

CALL_UPLOAD_ID = "audio_upload"


class CallState(rx.State):
    """State for the voice call interface."""

    is_recording: bool = False
    is_processing: bool = False
    error_message: str = ""
    audio_response_src: str = ""

    async def _generate_audio_response(self) -> str:
        """Generates a mock audio response using ElevenLabs."""
        menu_state = await self.get_state(MenuState)
        menu_items = []
        for section in menu_state.menu_data:
            for item in section["items"]:
                menu_items.append(item["name"])
        response_text = f"Hello! Welcome to the restaurant for menu {menu_state.current_menu_id}. Today we have {', '.join(menu_items[:3])} on the menu. Is there anything I can help you with?"
        try:
            api_key = os.getenv("ELEVEN_LABS_API_KEY")
            if not api_key:
                logging.error("ELEVEN_LABS_API_KEY not set.")
                self.error_message = "Audio generation service is not configured."
                return ""
            client = ElevenLabs(api_key=api_key)
            audio_generator = client.text_to_speech.convert(
                text=response_text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            timestamp = uuid.uuid4()
            filename = f"response_{timestamp}.mp3"
            outfile = rx.get_upload_dir() / filename
            with outfile.open("wb") as file_object:
                for chunk in audio_generator:
                    file_object.write(chunk)
            return filename
        except Exception as e:
            logging.exception(f"TTS Generation failed: {e}")
            self.error_message = "Sorry, I couldn't generate a response."
            return ""

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