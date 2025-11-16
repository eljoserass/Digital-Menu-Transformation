import reflex as rx
import asyncio
import os
from pathlib import Path
import logging
import reflex as rx
import asyncio
import os
from pathlib import Path
import logging
import uuid
import base64
from app.states.menu_state import MenuState



from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

from openai import OpenAI

CALL_UPLOAD_ID = "audio_upload"



def menu_to_str(menu_id: str) -> str:
    menu_path = Path("menus") / f"{menu_id}.json"
    print("MENU PATH = ", menu_path)
    if menu_path.exists():
        with open(menu_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

class CallState(rx.State):
    """State for the voice call interface."""

    is_recording: bool = False
    is_processing: bool = False
    error_message: str = ""
    audio_response_src: str = ""
    uploaded_audio_path: str = ""


    async def _generate_audio_response(self) -> str | None:
        """Generates a mock audio response by copying a sample file to a new unique path."""

        client = OpenAI()
        audio_file= open(self.uploaded_audio_path, "rb")

        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

        async with self:
            menu_state = await self.get_state(MenuState)

            

            stream = client.responses.create(
                model="gpt-4.1-mini-2025-04-14",
                input=[
                    {
                        "role":"system",
                        "content": "answer questions from the user about the menu, recommend it stuff. you will be the sommelier of it at a bar " + menu_to_str(menu_state.id)
                    },
                    {
                        "role": "user",
                        "content": transcription.text,
                    },
                ],
            )

        elevenlabs = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        

        audio = elevenlabs.text_to_speech.convert(
            text=stream.output_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        with open("output.mp3", "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        # await asyncio.sleep(2)
        # sample_audio_path = Path("assets") / "sample.mp3"
        # if not sample_audio_path.exists():
        #     logging.error("Sample audio file 'assets/sample.mp3' not found.")
        #     return None
        try:
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            unique_filename = f"response_{uuid.uuid4()}.mp3"
            new_audio_path = upload_dir / unique_filename
            with (
                new_audio_path.open("wb") as dest_file,
            ):
                for chunk in audio:
                    if chunk:
                        dest_file.write(chunk)
            return unique_filename
        except Exception as e:
            logging.exception(f"Failed to create mock audio response: {e}")
            return None

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
            print ("FILE PATH FOR THE AUDIO", file_path)
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.uploaded_audio_path = str(file_path)
            response_filename = await self._generate_audio_response()
            if response_filename:
                self.audio_response_src = response_filename
            else:
                self.error_message = "Could not generate audio response."
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