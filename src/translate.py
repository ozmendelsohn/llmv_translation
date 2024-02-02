import base64
import requests
import json
import logging
import os
import time

class OpenAITranslator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.endpoint = os.getenv('OPENAI_ENDPOINT', "https://api.openai.com/v1/chat/completions")

    @staticmethod
    def encode_image(image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            logging.error(f"File not found: {image_path}")
            return None

    def translate_image(self, base64_image, prompt, max_tokens=1000):
        # base64_image = self.encode_image(image_path)
        # if base64_image is None:
        #     return "Error: Image could not be processed."

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return "Error: Translation request failed."

# Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api_key = os.getenv('OPENAI_API_KEY') or json.load(open('/workspaces/llmv_translation/secrets.json'))['openai_api_key']
    translator = OpenAITranslator(api_key)

    image_path = "/workspaces/llmv_translation/images/1-14_rotated_page-0003.jpg"
    prompt = """
Please help me to translate the following book from English to Hebrew.
I am going to upload one page each messages then you will only write the translate version.
Please notice that sometimes a sentence will start in on page and will end in the next one, please wait for the full 
sentence in the text page than write it under the current page."""
    
    translation = translator.translate_image(image_path, prompt)
    print(translation)
