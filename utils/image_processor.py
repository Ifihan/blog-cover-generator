from PIL import Image, ImageDraw, ImageFont
import io

class ImageProcessor:
    @staticmethod
    def process_image(image_data, platform, custom_dims=None, text_overlay=None):
        """Resize/crop image to platform dimensions and add optional text overlay."""
        img = Image.open(io.BytesIO(image_data))

        # If platform is None, skip resizing and only apply text overlay
        if platform is not None:
            target_width, target_height = ImageProcessor._get_dimensions(platform, custom_dims)

            if target_width == 0 or target_height == 0:
                # If dimensions are invalid, only apply text overlay if provided
                if text_overlay and text_overlay.get('text'):
                    img = ImageProcessor._add_text_overlay(img, text_overlay)
                    output = io.BytesIO()
                    img.save(output, format='PNG')
                    return output.getvalue()
                return image_data

            img_ratio = img.width / img.height
            target_ratio = target_width / target_height

            if img_ratio > target_ratio:
                new_height = target_height
                new_width = int(new_height * img_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / img_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2

            img = img.crop((left, top, right, bottom))

        # Apply text overlay if provided
        if text_overlay and text_overlay.get('text'):
            img = ImageProcessor._add_text_overlay(img, text_overlay)

        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    @staticmethod
    def _add_text_overlay(img, text_overlay):
        """Add text overlay with automatic line wrapping."""
        draw = ImageDraw.Draw(img)
        text = text_overlay.get('text', '')
        font_name = text_overlay.get('font', 'Inter')
        size = text_overlay.get('size', 36)
        color = text_overlay.get('color', '#FFFFFF')
        position = text_overlay.get('position', 'bottom-center')
        shadow = text_overlay.get('shadow', True)
        font_paths = {
            'Inter': ['/System/Library/Fonts/Helvetica.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
            'Arial': ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'],
            'Helvetica': ['/System/Library/Fonts/Helvetica.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
            'Georgia': ['/System/Library/Fonts/Supplemental/Georgia.ttf', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'],
            'Times New Roman': ['/System/Library/Fonts/Supplemental/Times New Roman.ttf', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'],
            'Courier New': ['/System/Library/Fonts/Supplemental/Courier New.ttf', '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf'],
            'Verdana': ['/System/Library/Fonts/Supplemental/Verdana.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
            'Comic Sans MS': ['/System/Library/Fonts/Supplemental/Comic Sans MS.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'],
            'Impact': ['/System/Library/Fonts/Supplemental/Impact.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'],
            'Trebuchet MS': ['/System/Library/Fonts/Supplemental/Trebuchet MS.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
        }

        font = None
        font_paths_to_try = font_paths.get(font_name, font_paths['Inter'])

        for font_path in font_paths_to_try:
            try:
                font = ImageFont.truetype(font_path, size)
                break
            except:
                continue

        if font is None:
            font = ImageFont.load_default()

        img_width, img_height = img.size
        padding = int(img_width * 0.05)
        max_width = int(img_width * 0.9)

        lines = ImageProcessor._wrap_text(text, font, max_width, draw)

        line_height = int(size * 1.3)
        total_height = len(lines) * line_height

        align = 'center'
        if 'left' in position:
            align = 'left'
        elif 'right' in position:
            align = 'right'
        if 'top' in position:
            y = padding
        elif 'bottom' in position:
            y = img_height - total_height - padding
        else:
            y = (img_height - total_height) // 2

        shadow_offset = max(2, size // 18) if shadow else 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]

            if align == 'left':
                x = padding
            elif align == 'right':
                x = img_width - line_width - padding
            else:
                x = (img_width - line_width) // 2

            if shadow:
                draw.text(
                    (x + shadow_offset, y + shadow_offset),
                    line,
                    font=font,
                    fill='black'
                )

            draw.text((x, y), line, font=font, fill=color)

            y += line_height

        return img

    @staticmethod
    def _wrap_text(text, font, max_width, draw):
        """Wrap text to fit within max_width, preserving line breaks."""
        lines = []
        user_lines = text.split('\n')

        for user_line in user_lines:
            user_line = user_line.strip()
            if not user_line:
                lines.append('')
                continue

            bbox = draw.textbbox((0, 0), user_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                lines.append(user_line)
            else:
                words = user_line.split(' ')
                current_line = []

                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    test_width = bbox[2] - bbox[0]

                    if test_width <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)

                if current_line:
                    lines.append(' '.join(current_line))

        return lines

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
