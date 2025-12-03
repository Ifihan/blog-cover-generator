from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    url_for,
    session,
)
import uuid
import io
import base64
import logging
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import joinedload

from models import db, User, Generation, GeneratedImage, Feedback
from utils.image_generator import NanoBananaClient
from utils.image_processor import ImageProcessor
from utils.storage import GCSStorage

# Configure logging
logger = logging.getLogger(__name__)

# Lazy initialization for services
_client = None
_storage = None


def get_client():
    """Lazy initialization of NanoBananaClient."""
    global _client
    if _client is None:
        _client = NanoBananaClient()
    return _client


def get_storage():
    """Lazy initialization of GCSStorage."""
    global _storage
    if _storage is None:
        _storage = GCSStorage()
    return _storage


# In-memory storage for generated images (before saving to database)
GENERATED_IMAGES = {}

# Create blueprint
main_bp = Blueprint("main", __name__)


# ============================================================================
# Authentication Routes
# ============================================================================


@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.app_page"))

    if request.method == "POST":
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        # Save pending generation if exists
        pending_gen = session.get("pending_generation")
        if pending_gen and pending_gen["generation_id"] in GENERATED_IMAGES:
            selected_index = pending_gen.get("selected_index")

            if selected_index is not None:
                try:
                    generation_id = pending_gen["generation_id"]
                    images_data = GENERATED_IMAGES[generation_id]

                    if selected_index < len(images_data):
                        img_bytes = images_data[selected_index]

                        generation = Generation(
                            user_id=user.id,
                            title=pending_gen["title"],
                            style=pending_gen["style"],
                            draft_link=pending_gen.get("draft_link"),
                            generation_id=generation_id,
                        )
                        db.session.add(generation)

                        filename = f"{generation_id}.png"
                        storage_path = get_storage().upload_image(
                            img_bytes, filename, username=user.username
                        )

                        generated_image = GeneratedImage(
                            generation_id=generation_id,
                            image_url=storage_path,
                            index_number=0,
                        )
                        db.session.add(generated_image)
                        db.session.commit()

                    del GENERATED_IMAGES[generation_id]
                    session.pop("pending_generation", None)

                except Exception as e:
                    logger.error(f"Error saving pending generation: {e}")
                    db.session.rollback()

        return jsonify({"success": True, "redirect": url_for("main.app_page")})

    return render_template("signup.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.app_page"))

    if request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401

        login_user(user)
        return jsonify({"success": True, "redirect": url_for("main.app_page")})

    return render_template("login.html")


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.landing"))


# ============================================================================
# Page Routes
# ============================================================================


@main_bp.route("/")
def landing():
    return render_template("landing.html")


@main_bp.route("/app")
def app_page():
    return render_template("app.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Use joinedload to prevent N+1 queries
    user_generations = (
        Generation.query.filter_by(user_id=current_user.id)
        .options(joinedload(Generation.images))
        .order_by(Generation.created_at.desc())
        .all()
    )

    for generation in user_generations:
        for image in generation.images:
            if not image.image_url:
                image.display_url = None
                continue

            # Use the full storage path (e.g., "admin/uuid.png")
            image.display_url = url_for("main.serve_image", filename=image.image_url)

    return render_template("dashboard.html", generations=user_generations)


# ============================================================================
# API Routes - Image Generation
# ============================================================================


@main_bp.route("/api/generate", methods=["POST"])
def generate():
    """Generate blog cover images using AI."""
    data = request.json
    title = data.get("title")
    style = data.get("style")
    draft_link = data.get("draft_link")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        images_data = get_client().generate_images(title, style, draft_link)

        image_urls = []
        generation_id = str(uuid.uuid4())
        GENERATED_IMAGES[generation_id] = []

        for img_bytes in images_data:
            b64_img = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{b64_img}"
            image_urls.append(data_url)
            GENERATED_IMAGES[generation_id].append(img_bytes)

        session["pending_generation"] = {
            "generation_id": generation_id,
            "title": title,
            "style": style,
            "draft_link": draft_link,
        }

        return jsonify({"images": image_urls, "generation_id": generation_id})

    except Exception as e:
        logger.error(f"Error generating images: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/api/save-selection", methods=["POST"])
@login_required
def save_selection():
    """Save the user's selected image to database and GCS."""
    try:
        data = request.json
        generation_id = data.get("generation_id")
        selected_index = data.get("selected_index")

        pending_gen = session.get("pending_generation")
        if not pending_gen or pending_gen["generation_id"] != generation_id:
            return jsonify({"error": "Generation not found"}), 404

        if generation_id not in GENERATED_IMAGES:
            return jsonify({"error": "Images not available"}), 404

        if selected_index >= len(GENERATED_IMAGES[generation_id]):
            return jsonify({"error": "Invalid image index"}), 400

        img_bytes = GENERATED_IMAGES[generation_id][selected_index]

        generation = Generation(
            user_id=current_user.id,
            title=pending_gen["title"],
            style=pending_gen["style"],
            draft_link=pending_gen.get("draft_link"),
            generation_id=generation_id,
        )
        db.session.add(generation)

        filename = f"{generation_id}.png"
        storage_path = get_storage().upload_image(
            img_bytes, filename, username=current_user.username
        )

        generated_image = GeneratedImage(
            generation_id=generation_id,
            image_url=storage_path,
            index_number=0,
        )
        db.session.add(generated_image)
        db.session.commit()

        del GENERATED_IMAGES[generation_id]
        session.pop("pending_generation", None)

        return jsonify({"success": True, "message": "Image saved successfully"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving selection: {e}")
        return jsonify({"error": "Failed to save image"}), 500


@main_bp.route("/api/update-selection", methods=["POST"])
def update_selection():
    """Update the selected image index in session for guest users."""
    try:
        data = request.json
        generation_id = data.get("generation_id")
        selected_index = data.get("selected_index")

        pending_gen = session.get("pending_generation")
        if not pending_gen or pending_gen["generation_id"] != generation_id:
            return jsonify({"error": "Generation not found"}), 404

        pending_gen["selected_index"] = selected_index
        session["pending_generation"] = pending_gen
        session.modified = True

        return jsonify({"success": True})

    except Exception as e:
        logger.error(f"Error updating selection: {e}")
        return jsonify({"error": "Failed to update selection"}), 500


# ============================================================================
# API Routes - Image Processing & Download
# ============================================================================


@main_bp.route("/api/download", methods=["POST"])
def download():
    """Process and download image with optional text overlay and resizing."""
    data = request.json
    generation_id = data.get("generation_id")
    index = data.get("selected_image_index", 0)
    platform = data.get("platform")
    custom_dims = data.get("custom_dims")
    text_overlay = data.get("text_overlay")

    logger.info(f"Download request - platform: {platform}, text_overlay: {text_overlay}")

    if not generation_id:
        return jsonify({"error": "Invalid generation ID"}), 404

    try:
        # Get image bytes from memory or database
        if generation_id in GENERATED_IMAGES:
            original_image_bytes = GENERATED_IMAGES[generation_id][index]
        else:
            generation = Generation.query.filter_by(
                generation_id=generation_id
            ).first()

            if not generation:
                return jsonify({"error": "Invalid generation ID"}), 404

            images = sorted(generation.images, key=lambda img: img.index_number)

            if not images:
                return jsonify({"error": "No images found for this generation"}), 404

            image_record = images[0]

            original_image_bytes = get_storage().download_image(image_record.image_url)

            if not original_image_bytes:
                return jsonify({"error": "Image not found in storage"}), 404

        # Process image
        processed_image_bytes = ImageProcessor.process_image(
            original_image_bytes, platform, custom_dims, text_overlay
        )

        # If text overlay was applied and this is a saved generation, update the stored image
        if text_overlay and text_overlay.get('text') and generation_id not in GENERATED_IMAGES:
            try:
                generation = Generation.query.filter_by(
                    generation_id=generation_id
                ).first()

                if generation and generation.images:
                    # Get the original image with text overlay (no resizing)
                    image_with_text = ImageProcessor.process_image(
                        original_image_bytes,
                        platform=None,  # No resizing, just apply text
                        custom_dims=None,
                        text_overlay=text_overlay
                    )

                    # Update the stored image
                    image_record = generation.images[0]
                    filename = f"{generation_id}.png"
                    username = generation.user.username if generation.user else 'default'

                    get_storage().upload_image(
                        image_with_text, filename, username=username
                    )

                    logger.info(f"Updated stored image with text overlay for generation {generation_id}")
            except Exception as e:
                logger.error(f"Error updating stored image with text overlay: {e}")
                # Don't fail the download if storage update fails

        return send_file(
            io.BytesIO(processed_image_bytes),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"blog-cover-{platform.lower()}.png",
        )
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/images/<path:filename>")
@login_required
def serve_image(filename):
    """Serve images from GCS through Flask with authentication."""
    try:
        image_bytes = get_storage().download_image(filename)

        if image_bytes is None:
            return jsonify({"error": "Image not found"}), 404

        return send_file(
            io.BytesIO(image_bytes),
            mimetype="image/png",
            max_age=3600,
        )
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Failed to load image"}), 500


# ============================================================================
# API Routes - Generation Management
# ============================================================================


@main_bp.route("/api/generation/<generation_id>", methods=["DELETE"])
@login_required
def delete_generation(generation_id):
    """Delete a generation and all its images."""
    try:
        generation = Generation.query.filter_by(
            generation_id=generation_id, user_id=current_user.id
        ).first()

        if not generation:
            return jsonify({"error": "Generation not found"}), 404

        # Delete images from storage
        for image in generation.images:
            try:
                get_storage().delete_image(image.image_url)
            except Exception as e:
                logger.warning(f"Error deleting image from GCS: {e}")

        # Delete from database
        db.session.delete(generation)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "Generation deleted successfully"}
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting generation: {e}")
        return jsonify({"error": "Failed to delete generation"}), 500


# ============================================================================
# API Routes - Configuration
# ============================================================================


@main_bp.route("/api/styles", methods=["GET"])
def get_styles():
    """Get available image styles."""
    styles = [
        "Creative",
        "Cinematic",
        "Minimalist",
        "Professional",
        "Abstract",
        "Tech",
    ]
    return jsonify(styles)


@main_bp.route("/api/platforms", methods=["GET"])
def get_platforms():
    """Get available platform dimensions."""
    platforms = {
        "Hashnode": {"width": 1600, "height": 840},
        "Dev.to": {"width": 1000, "height": 420},
        "Medium": {"width": 1500, "height": 750},
        "Custom": {"width": 0, "height": 0},
    }
    return jsonify(platforms)


# ============================================================================
# API Routes - Feedback
# ============================================================================


@main_bp.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback."""
    data = request.json

    feedback_type = data.get("type")
    rating = data.get("rating")
    message = data.get("message")
    name = data.get("name")
    email = data.get("email")

    if not feedback_type or not message:
        return jsonify({"error": "Feedback type and message are required"}), 400

    feedback = Feedback(
        user_id=current_user.id if current_user.is_authenticated else None,
        name=name,
        email=email,
        feedback_type=feedback_type,
        rating=rating,
        message=message,
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({"success": True, "message": "Thank you for your feedback!"}), 201
