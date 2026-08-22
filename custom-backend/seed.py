from app import app, db
from models import User, File
from werkzeug.security import generate_password_hash
import os


# =========================
# TEST USERS
# =========================

users_data = [
    {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "Password123!"
    },
    {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "Password123!"
    },
    {
        "name": "Carol",
        "email": "carol@example.com",
        "password": "Password123!"
    }
]


# =========================
# SEED DATABASE
# =========================

with app.app_context():

    for user_data in users_data:

        user = User.query.filter_by(
            email=user_data["email"]
        ).first()

        if not user:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=generate_password_hash(
                    user_data["password"]
                )
            )

            db.session.add(user)
            db.session.commit()

            print("Created user:", user.email)

        else:
            print("User already exists:", user.email)


    # =========================
    # CREATE FILE RECORDS
    # =========================

    file_data = [
        ("alice@example.com", "alice_resume.pdf"),
        ("alice@example.com", "alice_notes.txt"),

        ("bob@example.com", "bob_resume.pdf"),
        ("bob@example.com", "bob_notes.txt"),

        ("carol@example.com", "carol_resume.pdf"),
        ("carol@example.com", "carol_notes.txt")
    ]


    for email, filename in file_data:

        user = User.query.filter_by(
            email=email
        ).first()

        existing_file = File.query.filter_by(
            user_id=user.id,
            filename=filename
        ).first()

        if not existing_file:

            new_file = File(
                user_id=user.id,
                filename=filename,
                stored_filename=filename
            )

            db.session.add(new_file)

            print(
                "Created file:",
                filename,
                "for",
                email
            )


    db.session.commit()

    print("\nSeeding completed successfully!")