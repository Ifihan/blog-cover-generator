from PIL import Image
import io

class ImageProcessor:
    @staticmethod
    def process_image(image_data, platform, custom_dims=None):
        """
        Resizes/crops the image to fit the target platform dimensions.
        image_data: bytes
        platform: str
        custom_dims: dict {'width': int, 'height': int}
        """
        img = Image.open(io.BytesIO(image_data))
        
        target_width, target_height = ImageProcessor._get_dimensions(platform, custom_dims)
        
        if target_width == 0 or target_height == 0:
            return image_data # Return original if no valid dimensions
            
        # Resize and Crop to fill
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider than target, crop width
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller than target, crop height
            new_width = target_width
            new_height = int(new_width / img_ratio)
            
        # High quality resize
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2
        
        img = img.crop((left, top, right, bottom))
        
        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    @staticmethod
    def _get_dimensions(platform, custom_dims):
        platforms = {
            "Hashnode": (1600, 840),
            "Dev.to": (1000, 420),
            "Medium": (1500, 750),
        }
        
        if platform == "Custom" and custom_dims:
            return int(custom_dims.get('width', 0)), int(custom_dims.get('height', 0))
            
        return platforms.get(platform, (0, 0))
