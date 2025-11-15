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

    is_processing: bool = False
    error_message: str = ""
    audio_response_src: str = ""

    async def _mock_audio_process(self, file: rx.UploadFile) -> str:
        """Mocks processing audio and generating a response using the menu."""
        await asyncio.sleep(2)
        menu_state = await self.get_state(MenuState)
        menu_items = []
        for section in menu_state.menu_data:
            for item in section["items"]:
                menu_items.append(item["name"])
        response_text = f"Hello! Welcome to the restaurant for menu {menu_state.current_menu_id}. Today we have {', '.join(menu_items[:3])} on the menu. Is there anything I can help you with?"
        try:
            client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))
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
    def reset_state(self):
        """Resets the call page to its initial state."""
        self.is_processing = False
        self.error_message = ""
        self.audio_response_src = ""
        return rx.clear_selected_files(CALL_UPLOAD_ID)

    @rx.event
    async def handle_audio_upload(self, files: list[rx.UploadFile]):
        """Handle the upload and processing of the recorded audio."""
        if not files:
            self.error_message = "No audio was recorded. Please try again."
            return
        self.is_processing = True
        self.error_message = ""
        self.audio_response_src = ""
        yield
        try:
            uploaded_file = files[0]
            response_filename = await self._mock_audio_process(uploaded_file)
            if response_filename:
                self.audio_response_src = response_filename
            else:
                pass
            self.is_processing = False
            yield
        except Exception as e:
            logging.exception(f"Audio processing failed: {e}")
            self.error_message = "An unexpected error occurred."
            self.is_processing = False
            yield