from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

import uuid
import io
import base64
from utils.image_generator import NanoBananaClient
from utils.image_processor import ImageProcessor

GENERATED_IMAGES = {}

client = NanoBananaClient()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/app')
def app_page():
    return render_template('app.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    title = data.get('title')
    style = data.get('style')
    draft_link = data.get('draft_link')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        images_data = client.generate_images(title, style, draft_link)
        
        image_urls = []
        generation_id = str(uuid.uuid4())
        GENERATED_IMAGES[generation_id] = []

        for img_bytes in images_data:
            b64_img = base64.b64encode(img_bytes).decode('utf-8')
            data_url = f"data:image/png;base64,{b64_img}"
            image_urls.append(data_url)
            GENERATED_IMAGES[generation_id].append(img_bytes)
            
        return jsonify({
            "images": image_urls,
            "generation_id": generation_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    generation_id = data.get('generation_id')
    index = data.get('selected_image_index', 0)
    platform = data.get('platform')
    custom_dims = data.get('custom_dims')
    text_overlay = data.get('text_overlay')

    if not generation_id or generation_id not in GENERATED_IMAGES:
        return jsonify({"error": "Invalid generation ID"}), 404

    try:
        original_image_bytes = GENERATED_IMAGES[generation_id][index]
        processed_image_bytes = ImageProcessor.process_image(original_image_bytes, platform, custom_dims, text_overlay)
        
        return send_file(
            io.BytesIO(processed_image_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name=f"blog-cover-{platform.lower()}.png"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/styles', methods=['GET'])
def get_styles():
    styles = [
        "Creative",
        "Cinematic",
        "Minimalist",
        "Professional",
        "Abstract",
        "Tech"
    ]
    return jsonify(styles)

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    platforms = {
        "Hashnode": {"width": 1600, "height": 840},
        "Dev.to": {"width": 1000, "height": 420},
        "Medium": {"width": 1500, "height": 750},
        "Custom": {"width": 0, "height": 0}
    }
    return jsonify(platforms)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
