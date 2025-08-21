import os
import base64
from cryptography.fernet import Fernet
from typing import Optional

# Generate or load encryption key from environment
def get_encryption_key() -> bytes:
    key = os.getenv("SETTINGS_ENCRYPTION_KEY")
    if not key:
        # Generate a new key (you should save this to your .env file)
        key = Fernet.generate_key().decode()
        print(f"Generated new encryption key. Add to .env: SETTINGS_ENCRYPTION_KEY={key}")
    return key.encode() if isinstance(key, str) else key

def encrypt_value(value: str) -> str:
    """Encrypt a setting value."""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(value.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a setting value."""
    f = Fernet(get_encryption_key())
    decoded = base64.b64decode(encrypted_value.encode())
    return f.decrypt(decoded).decode()

def get_setting(session, key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a setting value, decrypting if necessary."""
    from .models import Setting
    from sqlmodel import select
    
    stmt = select(Setting).where(Setting.key == key)
    setting = session.exec(stmt).first()
    
    if not setting:
        return default
    
    if setting.is_encrypted:
        return decrypt_value(setting.value)
    return setting.value

def set_setting(session, key: str, value: str, category: Optional[str] = None, 
                encrypt: bool = False, description: Optional[str] = None):
    """Set a setting value, encrypting if necessary."""
    from .models import Setting
    from datetime import datetime
    
    encrypted_value = encrypt_value(value) if encrypt else value
    
    setting = Setting(
        key=key,
        value=encrypted_value,
        category=category,
        is_encrypted=encrypt,
        description=description,
        updated_at=datetime.utcnow()
    )
    
    session.merge(setting)
    session.commit()