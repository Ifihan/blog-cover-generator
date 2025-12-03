import os
import base64
import logging
from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User
from routes import main_bp
from admin import admin_bp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    @app.template_filter("b64encode")
    def b64encode_filter(data):
        return base64.b64encode(data).decode("utf-8")

    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {error}")
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.getenv("PORT", 5001))
    app.run(debug=True, port=port, host="0.0.0.0")