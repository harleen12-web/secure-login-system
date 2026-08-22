from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from datetime import datetime, timedelta
from collections import defaultdict

# Load information from .env
load_dotenv()

# Create Flask application
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500",
        "http://localhost:5500"]
)
# Connect Flask to PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

from models import db, User, Session, File

db.init_app(app)

# =========================
# LOGIN RATE LIMITING
# =========================

failed_login_attempts = defaultdict(list)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5


# =========================
# GET MY FILES
# =========================

@app.route("/files", methods=["GET"])
def get_files():

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "Authentication required"
        }), 401

    files = File.query.filter_by(
        user_id=user.id
    ).all()

    result = []

    for file in files:
        result.append({
            "id": file.id,
            "filename": file.filename
        })

    return jsonify(result), 200


# =========================
# GET ONE FILE
# =========================

@app.route("/files/<int:file_id>", methods=["GET"])
def get_file(file_id):

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "Authentication required"
        }), 401

    file = File.query.filter_by(
        id=file_id
    ).first()

    if not file:
        return jsonify({
            "error": "File not found"
        }), 404

    if file.user_id != user.id:
        return jsonify({
            "error": "You do not have access to this file"
        }), 403

    return jsonify({
        "id": file.id,
        "filename": file.filename
    }), 200

# =========================
# DOWNLOAD FILE
# =========================

@app.route("/files/<int:file_id>/download", methods=["GET"])
def download_file(file_id):

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "Authentication required"
        }), 401

    file = File.query.filter_by(
        id=file_id
    ).first()

    if not file:
        return jsonify({
            "error": "File not found"
        }), 404

    if file.user_id != user.id:
        return jsonify({
            "error": "You do not have access to this file"
        }), 403

    return send_from_directory(
        "storage",
        file.stored_filename,
        as_attachment=True,
        download_name=file.filename
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout", methods=["POST"])
def logout():

    session_id = request.cookies.get("session_id")

    if session_id:

        session = Session.query.filter_by(
            session_id=session_id
        ).first()

        if session:
            session.revoked = True
            db.session.commit()

    response = jsonify({
        "message": "Logout successful"
    })

    response.delete_cookie("session_id")

    return response, 200


@app.route("/me", methods=["GET"])
def me():

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "Authentication required"
        }), 401

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    }), 200

# =========================
# AUTHENTICATION CHECK
# =========================

def get_current_user():

    session_id = request.cookies.get("session_id")

    if not session_id:
        return None

    session = Session.query.filter_by(
        session_id=session_id,
        revoked=False
    ).first()

    if not session:
        return None

    if session.expires_at < datetime.utcnow():
        session.revoked = True
        db.session.commit()
        return None

    user = User.query.get(session.user_id)

    return user

# =========================
# HOME ROUTE
# =========================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email", "").lower().strip()
    password = data.get("password")

    name = data.get(
        "name",
        email.split("@")[0]
    )

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Registration failed"
        }), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    }), 201

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").lower().strip()
    password = data.get("password")

    now = datetime.utcnow()

    recent_attempts = [
        attempt
        for attempt in failed_login_attempts[email]
        if now - attempt < timedelta(minutes=LOCKOUT_MINUTES)
    ]

    failed_login_attempts[email] = recent_attempts

    if len(recent_attempts) >= MAX_FAILED_ATTEMPTS:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not email or not password:
        failed_login_attempts[email].append(datetime.utcnow())

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        failed_login_attempts[email].append(datetime.utcnow())

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):
        failed_login_attempts[email].append(datetime.utcnow())

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Successful login
    failed_login_attempts[email].clear()

    session_id = secrets.token_urlsafe(32)

    new_session = Session(
        session_id=session_id,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=2),
        revoked=False
    )

    db.session.add(new_session)
    db.session.commit()

    response = jsonify({
        "message": "Login successful"
    })

    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="Lax",
        max_age=7200
    )

    return response, 200


@app.route("/")
def home():
    return "Flask backend is working!"


# =========================
# DATABASE TEST
# =========================

@app.route("/db-test")
def db_test():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "PostgreSQL connection is working!"
    except Exception as e:
        return f"Database connection failed: {e}", 500


# =========================
# CREATE DATABASE TABLES
# =========================

with app.app_context():
    db.create_all()


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    app.run(port=3000, debug=True)