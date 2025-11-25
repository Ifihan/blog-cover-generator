from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    url_for,
)
import os
import uuid
import io
import base64
from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import db, User, Generation, GeneratedImage
from utils.image_generator import NanoBananaClient
from utils.image_processor import ImageProcessor

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///blog_cover_generator.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_filter("b64encode")
def b64encode_filter(data):
    return base64.b64encode(data).decode("utf-8")


GENERATED_IMAGES = {}

client = NanoBananaClient()


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("app_page"))

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
        return jsonify({"success": True, "redirect": url_for("app_page")})

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("app_page"))

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
        return jsonify({"success": True, "redirect": url_for("app_page")})

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_generations = (
        Generation.query.filter_by(user_id=current_user.id)
        .order_by(Generation.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", generations=user_generations)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
def app_page():
    return render_template("app.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    title = data.get("title")
    style = data.get("style")
    draft_link = data.get("draft_link")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        images_data = client.generate_images(title, style, draft_link)

        image_urls = []
        generation_id = str(uuid.uuid4())
        GENERATED_IMAGES[generation_id] = []

        for img_bytes in images_data:
            b64_img = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{b64_img}"
            image_urls.append(data_url)
            GENERATED_IMAGES[generation_id].append(img_bytes)

        if current_user.is_authenticated:
            generation = Generation(
                user_id=current_user.id,
                title=title,
                style=style,
                draft_link=draft_link,
                generation_id=generation_id,
            )
            db.session.add(generation)

            for idx, img_bytes in enumerate(images_data):
                generated_image = GeneratedImage(
                    generation_id=generation_id, image_data=img_bytes, index_number=idx
                )
                db.session.add(generated_image)

            db.session.commit()

        return jsonify({"images": image_urls, "generation_id": generation_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def download():
    data = request.json
    generation_id = data.get("generation_id")
    index = data.get("selected_image_index", 0)
    platform = data.get("platform")
    custom_dims = data.get("custom_dims")
    text_overlay = data.get("text_overlay")

    if not generation_id or generation_id not in GENERATED_IMAGES:
        return jsonify({"error": "Invalid generation ID"}), 404

    try:
        original_image_bytes = GENERATED_IMAGES[generation_id][index]
        processed_image_bytes = ImageProcessor.process_image(
            original_image_bytes, platform, custom_dims, text_overlay
        )

        return send_file(
            io.BytesIO(processed_image_bytes),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"blog-cover-{platform.lower()}.png",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/styles", methods=["GET"])
def get_styles():
    styles = ["Creative", "Cinematic", "Minimalist", "Professional", "Abstract", "Tech"]
    return jsonify(styles)


@app.route("/api/platforms", methods=["GET"])
def get_platforms():
    platforms = {
        "Hashnode": {"width": 1600, "height": 840},
        "Dev.to": {"width": 1000, "height": 420},
        "Medium": {"width": 1500, "height": 750},
        "Custom": {"width": 0, "height": 0},
    }
    return jsonify(platforms)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
