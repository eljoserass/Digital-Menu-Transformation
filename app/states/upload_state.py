import reflex as rx
import asyncio
import json
import uuid
from pathlib import Path
import logging
import qrcode
from io import BytesIO
from openai import OpenAI
from pydantic import BaseModel

UPLOAD_ID = "menu_upload"
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class MenuItem(BaseModel):
    name: str
    price: float
    ingredients: list[str]
    allergens: list[str]


class MenuSection(BaseModel):
    title: str
    items: list[MenuItem]


class Menu(BaseModel):
    sections: list[MenuSection]


class UploadState(rx.State):
    """State for the menu upload page."""

    uploading: bool = False
    processing: bool = False
    error_message: str = ""
    qr_code_src: str = ""
    menu_url: str = ""

    async def _mock_llm_process(self, file_path: str) -> dict:
        """A mock function to simulate LLM processing of a menu image."""
        prompt = """

        parse the pictures of the menu by splitting it into Sections with its name

        each section has a list of items,
        with name -> simply the name of the item on the menu
        price -> the price of the food, it can be empty
        ingredients -> a list of ingredients of the food, if not explecitly stated just empty
        allergens -> if there is stated the allergens of a food add it



        """
        client_openai = OpenAI()
        encoded_image = encode_image(file_path)
        response = client_openai.responses.parse(
            model="gpt-4.1-2025-04-14",
            input=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "parse the menu"},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    ],
                },
            ],
            text_format=Menu,
        )
        event = response.output_parsed.dict()
        return event

    @rx.event
    def reset_state(self):
        """Resets the upload page to its initial state."""
        self.uploading = False
        self.processing = False
        self.error_message = ""
        self.qr_code_src = ""
        self.menu_url = ""
        return rx.clear_selected_files(UPLOAD_ID)

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload and processing of the menu image."""
        if not files:
            self.error_message = "Please select a file to upload."
            return
        self.uploading = True
        self.error_message = ""
        self.qr_code_src = ""
        yield
        try:
            uploaded_file = files[0]
            upload_data = await uploaded_file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            file_path = upload_dir / unique_filename
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.uploading = False
            self.processing = True
            yield
            processed_data = await self._mock_llm_process(file_path)
            menu_id = str(uuid.uuid4())[:8]
            menu_dir = Path("menus")
            menu_dir.mkdir(exist_ok=True)
            menu_file_path = menu_dir / f"{menu_id}.json"
            with menu_file_path.open("w") as f:
                json.dump(processed_data["sections"], f, indent=4)
            self.menu_url = f"{self.router.page.host}/menu/{menu_id}"
            qr_img = qrcode.make(self.menu_url)
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_code_data = buffer.getvalue()
            qr_filename = f"qr_{menu_id}.png"
            qr_path = upload_dir / qr_filename
            with qr_path.open("wb") as f:
                f.write(qr_code_data)
            self.processing = False
            self.qr_code_src = qr_filename
        except Exception as e:
            logging.exception(f"Upload failed: {e}")
            self.error_message = "An unexpected error occurred during upload."
            self.uploading = False
            self.processing = False
        finally:
            self.uploading = False
            self.processing = False
            yield