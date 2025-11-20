import os
import random
from google import genai
from google.genai import types
from PIL import Image
import io
import base64

class NanoBananaClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("NANO_BANANA_API_KEY")
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true" or not self.api_key
        
        if not self.mock_mode:
            self.client = genai.Client(api_key=self.api_key)

    def generate_images(self, title, style, draft_link=None, count=2):
        """Generate images based on title and style."""
        prompt = self._construct_prompt(title, style, draft_link)
        
        if self.mock_mode:
            return self._generate_mock_images(count)

        try:
            images = []
            for _ in range(count):
                response = self.client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                    )
                )

                for generated_image in response.generated_images:
                    images.append(generated_image.image)
                    
            return images
            
        except Exception as e:
            print(f"Error generating images: {e}")
            return self._generate_mock_images(count)

    def _construct_prompt(self, title, style, draft_link=None):
        base_prompt = f"A high quality, professional blog post cover image for an article titled '{title}'."

        if draft_link:
            base_prompt += f" (Reference: {draft_link})"

        style_prompts = {
            "Creative": "Artistic, abstract, colorful, creative composition, vibrant.",
            "Cinematic": "Cinematic lighting, dramatic, high contrast, movie poster style, 8k resolution.",
            "Minimalist": "Minimalist, clean lines, simple shapes, pastel colors, plenty of negative space.",
            "Professional": "Corporate, sleek, modern, business-oriented, blue and grey tones.",
            "Abstract": "Abstract shapes, geometric patterns, digital art, futuristic.",
            "Tech": "Technology focused, circuit boards, code snippets, cybernetic, neon lights."
        }

        style_instruction = style_prompts.get(style, "Clean and modern design.")
        return f"{base_prompt} Style: {style_instruction} No text on image."

    def _generate_mock_images(self, count):
        """Generate solid color placeholder images."""
        images = []
        for _ in range(count):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            img = Image.new('RGB', (1024, 1024), color=color)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            images.append(img_byte_arr.getvalue())

        return images
