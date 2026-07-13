"""AES-256-GCM token encryption for bank tokens."""

import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class TokenEncryption:
    """Encrypt/decrypt bank tokens using AES-256-GCM."""

    def __init__(self, key: Optional[bytes] = None):
        """Initialize with a 32-byte key.

        Args:
            key: 32-byte encryption key. If not provided, reads from
                 BANK_TOKEN_ENCRYPTION_KEY env var (must be base64-encoded
                 or exactly 32 bytes).
        """
        if key is None:
            key_str = os.getenv("BANK_TOKEN_ENCRYPTION_KEY", "")
            if not key_str:
                raise ValueError(
                    "BANK_TOKEN_ENCRYPTION_KEY environment variable is required"
                )
            # Try base64 first, then use raw bytes if exactly 32 chars
            try:
                key = base64.b64decode(key_str)
            except Exception:
                key = key_str.encode("utf-8")

        if len(key) != 32:
            raise ValueError(
                f"Encryption key must be exactly 32 bytes, got {len(key)}"
            )

        self._aesgcm = AESGCM(key)

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt a plaintext string and return bytes (nonce + ciphertext + tag).

        Returns:
            bytes: 12-byte nonce + AES-GCM ciphertext with authentication tag.
        """
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt bytes back to plaintext string.

        Args:
            ciphertext: 12-byte nonce + AES-GCM ciphertext with tag.

        Returns:
            Decrypted plaintext string.
        """
        if len(ciphertext) < 13:
            raise ValueError("Ciphertext too short")
        nonce = ciphertext[:12]
        encrypted = ciphertext[12:]
        plaintext = self._aesgcm.decrypt(nonce, encrypted, None)
        return plaintext.decode("utf-8")

    def encrypt_to_hex(self, plaintext: str) -> str:
        """Encrypt and return as hex string for easy storage."""
        return self.encrypt(plaintext).hex()

    def decrypt_from_hex(self, ciphertext_hex: str) -> str:
        """Decrypt from hex string."""
        return self.decrypt(bytes.fromhex(ciphertext_hex))
