
import hashlib
import secrets
from database import connect_db


# -----------------------------
# PASSWORD HASHING
# -----------------------------

def hash_password(password, salt=None):
    """Hash a password using SHA-256 and a unique salt."""

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.sha256(
        (salt + password).encode("utf-8")
    ).hexdigest()

    return password_hash, salt


# -----------------------------
# USER REGISTRATION
# -----------------------------

def register_user(username, email, password):
    """Register a new user."""

    if not username or not email or not password:
        return False, "All fields are required."

    password_hash, salt = hash_password(password)

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (
                username,
                email,
                password_hash,
                salt
            )
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, salt))

        connection.commit()

        return True, "Registration successful!"

    except Exception as error:

        if "UNIQUE constraint failed" in str(error):
            return False, "Username or email already exists."

        return False, "Registration failed."

    finally:
        connection.close()


# -----------------------------
# USER LOGIN
# -----------------------------

def login_user(username_or_email, password):
    """Verify login using either username or email."""

    if not username_or_email or not password:
        return False, "Please enter your username/email and password."

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, password_hash, salt
            FROM users
            WHERE username = ? OR email = ?
        """, (username_or_email, username_or_email))

        user = cursor.fetchone()

    finally:
        connection.close()

    if user is None:
        return False, "Account not found."

    user_id, stored_hash, salt = user

    entered_hash, _ = hash_password(password, salt)

    if secrets.compare_digest(entered_hash, stored_hash):
        return True, "Login successful!"

    return False, "Incorrect password."
