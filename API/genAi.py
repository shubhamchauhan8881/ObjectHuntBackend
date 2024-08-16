import google.generativeai as genai
import os
from PIL import Image
import typing_extensions as typing

class Recipe(typing.TypedDict):
  answer: bool

class Generator:
    genai = genai
    def __init__(self, api_key):
        self.genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={
                "response_mime_type": "application/json",
                "temperature":0.5,
                "response_schema": list[Recipe],
            }
        )

    def recognizeObject(self, prompt, image=None):
        response = self.model.generate_content([f"can you see {prompt} in this photo", image])
        return response.text