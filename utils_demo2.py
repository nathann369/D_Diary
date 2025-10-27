import json, os, hashlib, base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def hash_password(password: str) -> str:
    """Generate a PBKDF2 hashed password."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return f"{base64.urlsafe_b64encode(salt).decode()}${key.decode()}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a provided password against a stored PBKDF2 hash."""
    salt_b64, key_b64 = stored_password.split('$')
    salt = base64.urlsafe_b64decode(salt_b64)
    stored_key = base64.urlsafe_b64decode(key_b64)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    try:
        kdf.verify(provided_password.encode(), stored_key)
        return True
    except Exception:
        return False


def load_user_data(username: str) -> dict:
    """Load user's diary data."""
    file_name = f"data_{username}.json"
    if not os.path.exists(file_name):
        return {"entries": []}
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(username: str, data: dict):
    """Save user's diary data."""
    file_name = f"data_{username}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
