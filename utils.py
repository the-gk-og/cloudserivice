import os
import secrets
from datetime import datetime
from cryptography.fernet import Fernet

def generate_encryption_key():
    """Generate a new encryption key for a user"""
    return Fernet.generate_key()

def encrypt_text(text, key):
    """Encrypt text using Fernet symmetric encryption"""
    if isinstance(key, str):
        key = key.encode()
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, key):
    """Decrypt text using Fernet symmetric encryption"""
    if isinstance(key, str):
        key = key.encode()
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def format_date(date_string):
    """Format date string for display"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return date_string

def generate_secure_filename(user_id, original_filename):
    """Generate a secure filename for uploads"""
    from werkzeug.utils import secure_filename
    secure_name = secure_filename(original_filename)
    unique_id = secrets.token_hex(8)
    return f"{user_id}_{unique_id}_{secure_name}"

def allowed_file_type(filename, allowed_extensions):
    """Check if file type is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)