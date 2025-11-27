from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Generation, GeneratedImage, Feedback
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from utils.storage import GCSStorage

storage = GCSStorage()

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("landing"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template("admin_dashboard.html")


@admin_bp.route("/api/stats")
@admin_required
def get_stats():
    total_users = User.query.count()
    total_generations = Generation.query.count()
    total_images = GeneratedImage.query.count()

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    users_today = User.query.filter(func.date(User.created_at) == today).count()

    users_this_week = User.query.filter(User.created_at >= week_ago).count()

    users_this_month = User.query.filter(User.created_at >= month_ago).count()

    generations_today = Generation.query.filter(
        func.date(Generation.created_at) == today
    ).count()

    generations_this_week = Generation.query.filter(
        Generation.created_at >= week_ago
    ).count()

    generations_this_month = Generation.query.filter(
        Generation.created_at >= month_ago
    ).count()

    return jsonify(
        {
            "total_users": total_users,
            "total_generations": total_generations,
            "total_images": total_images,
            "users_today": users_today,
            "users_this_week": users_this_week,
            "users_this_month": users_this_month,
            "generations_today": generations_today,
            "generations_this_week": generations_this_week,
            "generations_this_month": generations_this_month,
        }
    )


@admin_bp.route("/api/recent-users")
@admin_required
def get_recent_users():
    users = User.query.order_by(desc(User.created_at)).limit(10).all()

    return jsonify(
        [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "generation_count": len(user.generations),
            }
            for user in users
        ]
    )


@admin_bp.route("/api/recent-generations")
@admin_required
def get_recent_generations():
    generations = Generation.query.order_by(desc(Generation.created_at)).limit(10).all()

    return jsonify(
        [
            {
                "id": gen.id,
                "username": gen.user.username,
                "title": gen.title,
                "style": gen.style,
                "created_at": gen.created_at.isoformat(),
                "image_count": len(gen.images),
            }
            for gen in generations
        ]
    )


@admin_bp.route("/api/style-distribution")
@admin_required
def get_style_distribution():
    styles = (
        db.session.query(Generation.style, func.count(Generation.id).label("count"))
        .group_by(Generation.style)
        .all()
    )

    return jsonify([{"style": style, "count": count} for style, count in styles])


@admin_bp.route("/api/user-activity")
@admin_required
def get_user_activity():
    days = 30
    data = []

    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=days - i - 1)

        users_count = User.query.filter(func.date(User.created_at) == date).count()

        generations_count = Generation.query.filter(
            func.date(Generation.created_at) == date
        ).count()

        data.append(
            {
                "date": date.isoformat(),
                "users": users_count,
                "generations": generations_count,
            }
        )

    return jsonify(data)


@admin_bp.route("/api/top-users")
@admin_required
def get_top_users():
    users = (
        db.session.query(User, func.count(Generation.id).label("generation_count"))
        .join(Generation)
        .group_by(User.id)
        .order_by(desc("generation_count"))
        .limit(10)
        .all()
    )

    return jsonify(
        [
            {
                "username": user.username,
                "email": user.email,
                "generation_count": count,
                "created_at": user.created_at.isoformat(),
            }
            for user, count in users
        ]
    )


@admin_bp.route("/api/users")
@admin_required
def get_all_users():
    users = User.query.order_by(desc(User.created_at)).all()

    return jsonify(
        [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
                "generation_count": len(user.generations),
            }
            for user in users
        ]
    )


@admin_bp.route("/api/users/<int:user_id>/promote", methods=["POST"])
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()

    return jsonify({"success": True, "message": f"{user.username} is now an admin"})


@admin_bp.route("/api/users/<int:user_id>/demote", methods=["POST"])
@admin_required
def demote_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({"success": False, "error": "You cannot demote yourself"}), 400

    user.is_admin = False
    db.session.commit()

    return jsonify(
        {"success": True, "message": f"{user.username} is no longer an admin"}
    )


@admin_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({"success": False, "error": "You cannot delete yourself"}), 400

    username = user.username

    try:
        storage.delete_user_folder(username)
    except Exception as e:
        print(f"Error deleting user folder from GCS: {e}")

    db.session.delete(user)
    db.session.commit()

    return jsonify({"success": True, "message": f"User {username} has been deleted"})


@admin_bp.route("/api/feedback")
@admin_required
def get_feedback():
    status_filter = request.args.get("status")

    query = Feedback.query

    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)

    feedback_list = query.order_by(desc(Feedback.created_at)).all()

    return jsonify(
        [
            {
                "id": fb.id,
                "type": fb.feedback_type,
                "rating": fb.rating,
                "message": fb.message,
                "status": fb.status,
                "created_at": fb.created_at.isoformat(),
                "user": {
                    "username": fb.user.username if fb.user else fb.name or "Anonymous",
                    "email": fb.user.email if fb.user else fb.email,
                },
            }
            for fb in feedback_list
        ]
    )


@admin_bp.route("/api/feedback/<int:feedback_id>/status", methods=["PUT"])
@admin_required
def update_feedback_status(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    data = request.json
    new_status = data.get("status")

    if new_status not in ["new", "in-progress", "resolved", "closed"]:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    feedback.status = new_status
    db.session.commit()

    return jsonify({"success": True, "message": "Status updated successfully"})


@admin_bp.route("/api/feedback/<int:feedback_id>", methods=["DELETE"])
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    db.session.delete(feedback)
    db.session.commit()

    return jsonify({"success": True, "message": "Feedback deleted successfully"})
