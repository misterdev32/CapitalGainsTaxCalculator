"""
Secrets management for secure storage of sensitive data.
"""

import base64
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecretsManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize secrets manager with encryption key."""
        self.encryption_key = encryption_key or self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> str:
        """Get or create encryption key."""
        key_file = Path("data/.encryption_key")
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        
        # Create new key
        key = Fernet.generate_key()
        
        # Ensure data directory exists
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save key securely
        with open(key_file, "wb") as f:
            f.write(key)
        
        # Set restrictive permissions
        key_file.chmod(0o600)
        
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def store_secret(self, key: str, value: str) -> None:
        """Store encrypted secret."""
        secrets_file = Path("data/.secrets")
        secrets = self._load_secrets()
        
        secrets[key] = self.encrypt(value)
        self._save_secrets(secrets)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get decrypted secret."""
        secrets = self._load_secrets()
        encrypted_value = secrets.get(key)
        
        if encrypted_value is None:
            return None
        
        try:
            return self.decrypt(encrypted_value)
        except ValueError:
            return None
    
    def delete_secret(self, key: str) -> None:
        """Delete secret."""
        secrets = self._load_secrets()
        if key in secrets:
            del secrets[key]
            self._save_secrets(secrets)
    
    def _load_secrets(self) -> dict:
        """Load secrets from file."""
        secrets_file = Path("data/.secrets")
        
        if not secrets_file.exists():
            return {}
        
        try:
            import json
            with open(secrets_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_secrets(self, secrets: dict) -> None:
        """Save secrets to file."""
        secrets_file = Path("data/.secrets")
        
        # Ensure data directory exists
        secrets_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(secrets_file, "w") as f:
            json.dump(secrets, f, indent=2)
        
        # Set restrictive permissions
        secrets_file.chmod(0o600)


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def store_api_credentials(exchange: str, api_key: str, api_secret: str) -> None:
    """Store encrypted API credentials."""
    manager = get_secrets_manager()
    manager.store_secret(f"{exchange}_api_key", api_key)
    manager.store_secret(f"{exchange}_api_secret", api_secret)
    print(f"✅ {exchange} API credentials stored securely")


def get_api_credentials(exchange: str) -> tuple[Optional[str], Optional[str]]:
    """Get decrypted API credentials."""
    manager = get_secrets_manager()
    api_key = manager.get_secret(f"{exchange}_api_key")
    api_secret = manager.get_secret(f"{exchange}_api_secret")
    return api_key, api_secret


def delete_api_credentials(exchange: str) -> None:
    """Delete API credentials."""
    manager = get_secrets_manager()
    manager.delete_secret(f"{exchange}_api_key")
    manager.delete_secret(f"{exchange}_api_secret")
    print(f"✅ {exchange} API credentials deleted")
