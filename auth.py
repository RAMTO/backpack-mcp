"""
Backpack Exchange API Authentication Helper

This module provides functions to sign requests for the Backpack Exchange API
using ED25519 keypairs.
"""

import base64
import time
from urllib.parse import urlencode
from cryptography.hazmat.primitives.asymmetric import ed25519


class BackpackAuth:
    """Helper class for signing Backpack Exchange API requests."""
    
    def __init__(self, private_key_b64: str, public_key_b64: str):
        """
        Initialize with base64-encoded ED25519 keys.
        
        Args:
            private_key_b64: Base64-encoded private key (seed)
            public_key_b64: Base64-encoded public key (verifying key)
        """
        private_key_bytes = base64.b64decode(private_key_b64)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        self.public_key_b64 = public_key_b64
    
    def sign_request(
        self,
        instruction: str,
        params: dict = None,
        timestamp: int = None,
        window: int = 5000,
        debug: bool = False
    ) -> dict:
        """
        Generate authentication headers for a signed request.
        
        Args:
            instruction: Instruction type (e.g., 'accountQuery', 'orderExecute')
            params: Request parameters (body or query params) as dict
            timestamp: Unix timestamp in milliseconds (defaults to current time)
            window: Time window in milliseconds (default: 5000, max: 60000)
            debug: If True, print the signing string for debugging
        
        Returns:
            Dictionary with headers: X-API-Key, X-Signature, X-Timestamp, X-Window
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        signing_string = self._build_signing_string(instruction, params, timestamp, window)
        
        if debug:
            print(f"Signing string: {signing_string}")
        
        signature_bytes = self.private_key.sign(signing_string.encode('utf-8'))
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        return {
            'X-API-Key': self.public_key_b64,
            'X-Signature': signature_b64,
            'X-Timestamp': str(timestamp),
            'X-Window': str(window)
        }
    
    def _build_signing_string(
        self,
        instruction: str,
        params: dict,
        timestamp: int,
        window: int
    ) -> str:
        """
        Build the string to be signed according to Backpack API spec.
        
        Process:
        1. Order params alphabetically and convert to query string
        2. Append timestamp and window
        3. Prefix with instruction type
        """
        parts = [f'instruction={instruction}']
        
        if params:
            sorted_params = sorted(params.items())
            param_string = urlencode(sorted_params)
            if param_string:
                parts.append(param_string)
        
        parts.append(f'timestamp={timestamp}')
        parts.append(f'window={window}')
        
        return '&'.join(parts)


def create_auth_from_env() -> BackpackAuth:
    """
    Create BackpackAuth instance from environment variables.
    
    Reads the following environment variables from .env file:
    - BACKPACK_PRIVATE_KEY: Base64-encoded ED25519 private key
    - BACKPACK_PUBLIC_KEY: Base64-encoded ED25519 public key
    
    Returns:
        BackpackAuth instance
    
    Raises:
        ValueError: If required environment variables are missing
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    private_key = os.getenv('BACKPACK_PRIVATE_KEY')
    public_key = os.getenv('BACKPACK_PUBLIC_KEY')
    
    if not private_key:
        raise ValueError(
            "Missing private key. Set BACKPACK_PRIVATE_KEY in .env file"
        )
    
    if not public_key:
        raise ValueError(
            "Missing public key. Set BACKPACK_PUBLIC_KEY in .env file"
        )
    
    return BackpackAuth(private_key, public_key)
