import os
import random
from google import genai
from PIL import Image
import io

class NanoBananaClient:
    """Client for generating blog cover images using Google's Gemini 2.5 Flash Image (NanoBanana) model."""

    # Correct NanoBanana (Gemini 2.5 Flash Image) model identifier
    MODEL_NAME = 'gemini-2.5-flash-image'

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true" or not self.api_key

        if not self.mock_mode:
            self.client = genai.Client(api_key=self.api_key)
        else:
            print("Running in MOCK MODE - using placeholder images")

    def generate_images(self, title, style, draft_link=None, count=2):
        """
        Generate blog cover images based on title and style.

        Args:
            title (str): The blog post title
            style (str): Visual style (Creative, Cinematic, Minimalist, Professional, Abstract, Tech)
            draft_link (str, optional): Link to draft article for context
            count (int): Number of images to generate (default: 2)

        Returns:
            list: List of image bytes
        """
        prompt = self._construct_prompt(title, style, draft_link)

        if self.mock_mode:
            return self._generate_mock_images(count)

        try:
            images = []
            for i in range(count):
                print(f"Generating image {i+1}/{count} with NanoBanana (Gemini 2.5 Flash Image)...")

                # NanoBanana uses generate_content, not generate_images
                response = self.client.models.generate_content(
                    model=self.MODEL_NAME,
                    contents=[prompt],
                )

                # Extract image from response
                for part in response.parts:
                    if part.inline_data is not None:
                        # The inline_data.data contains the raw image bytes
                        image_bytes = part.inline_data.data
                        images.append(image_bytes)
                        print(f"✓ Image {i+1} generated successfully")
                        break  # Only take first image from response

            return images

        except Exception as e:
            print(f"✗ Error generating images with NanoBanana: {e}")
            print("Falling back to mock images...")
            return self._generate_mock_images(count)

    def _construct_prompt(self, title, style, draft_link=None):
        """
        Construct optimized prompts for NanoBanana (Gemini 2.5 Flash Image) based on title and style.

        NanoBanana performs best with:
        - Detailed, descriptive language
        - Specific visual elements and composition
        - Clear lighting and atmosphere descriptions
        - Concrete subjects rather than abstract concepts
        - Natural language instructions
        """

        # Enhanced style-specific prompts optimized for Imagen 3.0
        style_prompts = {
            "Creative": {
                "description": "A vibrant, artistic blog cover with bold abstract shapes and flowing organic forms. "
                              "Rich saturated colors including deep purples, electric blues, warm oranges, and bright yellows. "
                              "Dynamic composition with layered geometric and fluid elements creating visual depth. "
                              "Modern digital art aesthetic with smooth gradients and textured brush strokes. "
                              "Professional lighting with soft shadows and glowing highlights.",
                "keywords": "creative, artistic, vibrant, abstract art, colorful, energetic, contemporary"
            },
            "Cinematic": {
                "description": "A dramatic, cinematic blog cover with epic movie poster composition. "
                              "Atmospheric lighting with strong contrasts between light and shadow, creating depth and mood. "
                              "Rich color grading with deep blacks, luminous highlights, and cinematic teal-orange tones. "
                              "Professional photography quality with sharp focus, bokeh background blur, and lens flare effects. "
                              "Wide-angle perspective with dynamic angles and powerful visual hierarchy.",
                "keywords": "cinematic, dramatic, high contrast, epic, atmospheric, professional photography, moody"
            },
            "Minimalist": {
                "description": "A clean, minimalist blog cover with elegant simplicity and sophisticated restraint. "
                              "Soft pastel color palette with gentle blues, blush pinks, sage greens, and cream whites. "
                              "Generous negative space creating breathing room and visual calm. "
                              "Simple geometric shapes with clean lines and subtle gradients. "
                              "Balanced composition with careful alignment and harmonious proportions. "
                              "Soft, diffused lighting with no harsh shadows.",
                "keywords": "minimalist, clean, simple, elegant, spacious, modern, sophisticated, gentle"
            },
            "Professional": {
                "description": "A polished, corporate blog cover with business-professional aesthetic. "
                              "Cool color palette dominated by navy blues, slate grays, and crisp whites with subtle teal accents. "
                              "Sleek, modern design with structured composition and geometric precision. "
                              "Clean professional photography style with sharp details and perfect lighting. "
                              "Subtle depth through layered elements, refined gradients, and sophisticated textures. "
                              "Corporate modern aesthetic suitable for business and technology contexts.",
                "keywords": "professional, corporate, business, sleek, modern, polished, sophisticated, clean"
            },
            "Abstract": {
                "description": "A futuristic, abstract blog cover with bold geometric patterns and digital art elements. "
                              "Complex layered shapes including triangles, circles, hexagons, and flowing curves. "
                              "Vibrant color combinations with gradient transitions and luminous effects. "
                              "3D rendered appearance with depth, shadows, and reflective surfaces. "
                              "Modern digital aesthetic with sharp edges, smooth curves, and dynamic movement. "
                              "Sci-fi inspired with technological and mathematical precision.",
                "keywords": "abstract, geometric, futuristic, digital art, 3D, modern, dynamic, colorful"
            },
            "Tech": {
                "description": "A high-tech blog cover with cutting-edge technology and digital innovation themes. "
                              "Dark background with electric neon accents in cyan blue, electric purple, and bright green. "
                              "Futuristic elements including circuit board patterns, glowing data streams, holographic interfaces, "
                              "and digital grid structures. Cyberpunk aesthetic with matrix-style code snippets and network nodes. "
                              "Sleek metallic surfaces with reflections and LED lighting effects. "
                              "Modern technological atmosphere with depth and luminous highlights.",
                "keywords": "technology, tech, futuristic, cyberpunk, neon, digital, high-tech, innovation, sci-fi"
            }
        }

        # Get style configuration
        style_config = style_prompts.get(style, {
            "description": "A modern, professional blog cover with clean design and balanced composition. "
                          "Appealing color palette and professional quality with good lighting.",
            "keywords": "modern, professional, clean, balanced"
        })

        # Extract topic/theme from title for context
        title_lower = title.lower()

        # Build the comprehensive prompt
        prompt_parts = [
            f"Create a professional blog cover image representing the topic: '{title}'.",
            style_config["description"],
            "The image should be visually striking and immediately capture attention.",
            "High resolution, photorealistic quality with perfect composition and professional color grading.",
            "Ensure the design leaves space for text overlay (no text should be included in the image itself).",
            f"Visual keywords: {style_config['keywords']}"
        ]

        final_prompt = " ".join(prompt_parts)

        # Add aspect ratio reminder for blog cover format
        final_prompt += " Widescreen horizontal format, 16:9 aspect ratio, suitable for blog header."

        return final_prompt

    def _generate_mock_images(self, count):
        """
        Generate realistic placeholder images for testing/development.
        Creates gradient images in 16:9 aspect ratio.
        """
        images = []
        # Blog cover standard size (16:9 aspect ratio)
        width, height = 1600, 900

        for i in range(count):
            # Create gradient background
            img = Image.new('RGB', (width, height))
            pixels = img.load()

            # Generate different color schemes for variety
            color_schemes = [
                ((99, 102, 241), (139, 92, 246)),  # Blue to Purple
                ((236, 72, 153), (251, 146, 60)),  # Pink to Orange
                ((59, 130, 246), (16, 185, 129)),  # Blue to Green
                ((168, 85, 247), (236, 72, 153)),  # Purple to Pink
                ((14, 165, 233), (99, 102, 241)),  # Cyan to Blue
            ]

            color1, color2 = color_schemes[i % len(color_schemes)]

            # Create horizontal gradient
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

                for y in range(height):
                    pixels[x, y] = (r, g, b)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            images.append(img_byte_arr.getvalue())

        return images
