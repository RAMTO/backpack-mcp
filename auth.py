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
        # Decode and load the private key
        private_key_bytes = base64.b64decode(private_key_b64)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        
        # Store public key for API header
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
        
        # Build signing string
        signing_string = self._build_signing_string(instruction, params, timestamp, window)
        
        if debug:
            print(f"Signing string: {signing_string}")
        
        # Sign the string
        signature_bytes = self.private_key.sign(signing_string.encode('utf-8'))
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        # Return headers
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
        # Start with instruction prefix
        parts = [f'instruction={instruction}']
        
        # Add parameters if they exist (ordered alphabetically)
        if params:
            # Sort params alphabetically and convert to query string format
            sorted_params = sorted(params.items())
            param_string = urlencode(sorted_params)
            if param_string:
                parts.append(param_string)
        
        # Append timestamp and window
        parts.append(f'timestamp={timestamp}')
        parts.append(f'window={window}')
        
        # Join with &
        return '&'.join(parts)


def create_auth_from_env() -> BackpackAuth:
    """
    Create BackpackAuth instance from environment variables.
    
    Supports multiple environment variable names:
    - Public key: BACKPACK_PUBLIC_KEY or BACKPACK_API_KEY
    - Private key: BACKPACK_PRIVATE_KEY or BACKPACK_SECRET_KEY
    
    Returns:
        BackpackAuth instance
    """
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Try multiple possible names for private key
    private_key = (
        os.getenv('BACKPACK_PRIVATE_KEY') or 
        os.getenv('BACKPACK_SECRET_KEY')
    )
    
    # Try multiple possible names for public key
    public_key = (
        os.getenv('BACKPACK_PUBLIC_KEY') or 
        os.getenv('BACKPACK_API_KEY')
    )
    
    if not private_key:
        raise ValueError(
            "Missing private key. Set BACKPACK_PRIVATE_KEY or BACKPACK_SECRET_KEY"
        )
    
    if not public_key:
        raise ValueError(
            "Missing public key. Set BACKPACK_PUBLIC_KEY or BACKPACK_API_KEY"
        )
    
    return BackpackAuth(private_key, public_key)
