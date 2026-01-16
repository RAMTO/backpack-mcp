"""
Backpack Exchange API Client

Wrapper around the Backpack API that handles authentication,
HTTP requests, and error handling.

Phase 2: Client with get_orders() method
"""

import requests
from typing import Optional, List, Dict, Any
from auth import create_auth_from_env


class BackpackClient:
    """
    Client for interacting with the Backpack Exchange API.
    
    Handles authentication, request signing, and error handling.
    All methods return clean data structures or raise exceptions.
    """
    
    def __init__(self, base_url: str = "https://api.backpack.exchange"):
        """
        Initialize the Backpack client.
        
        Args:
            base_url: Base URL for the Backpack API (default: production API)
        """
        # Create auth instance from environment variables
        # This loads BACKPACK_PRIVATE_KEY and BACKPACK_PUBLIC_KEY from .env
        self.auth = create_auth_from_env()
        self.base_url = base_url
    
    def get_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open spot orders, optionally filtered by symbol.
        
        Retrieves all open orders for SPOT markets. If symbol is provided,
        only returns orders for that trading pair.
        
        Args:
            symbol: Optional trading pair symbol (e.g., "BTC_USDC").
                   If None, returns all open spot orders.
        
        Returns:
            List of order dictionaries, each containing:
            - id: Order ID
            - symbol: Trading pair
            - side: "Bid" (buy) or "Ask" (sell)
            - orderType: "Limit", "Market", etc.
            - status: Order status
            - quantity: Order quantity
            - executedQuantity: Filled quantity
            - price: Limit price (if applicable)
            - timeInForce: "GTC", "IOC", etc.
            - createdAt: Timestamp in milliseconds
        
        Raises:
            ValueError: If API returns an error response
            requests.RequestException: If network request fails
        """
        # Build query parameters
        # marketType is REQUIRED - use 'SPOT' for spot orders
        query_params: Dict[str, str] = {
            'marketType': 'SPOT'
        }
        
        # Add optional symbol filter
        if symbol:
            query_params['symbol'] = symbol
        
        # Generate signed headers
        # For GET requests with query params, pass them to sign_request
        # Instruction: 'orderQueryAll' (from Backpack API docs)
        headers = self.auth.sign_request(
            instruction='orderQueryAll',
            params=query_params,
            window=5000
        )
        
        # Make GET request with query parameters
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/orders",
                params=query_params,
                headers=headers,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            orders = response.json()
            
            # Ensure we return a list (API might return empty list or dict)
            if isinstance(orders, list):
                return orders
            elif isinstance(orders, dict):
                # If API returns a dict, try to extract orders list
                if 'orders' in orders:
                    return orders['orders']
                else:
                    # Return as single-item list if it's an order object
                    return [orders]
            else:
                # Unexpected format, return empty list
                return []
                
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (4xx, 5xx)
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                if isinstance(error_detail, dict) and 'message' in error_detail:
                    error_msg += f": {error_detail['message']}"
                else:
                    error_msg += f": {response.text[:200]}"
            except:
                error_msg += f": {response.text[:200]}"
            raise ValueError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            # Handle network errors (connection, timeout, etc.)
            raise ValueError(f"Network error: {str(e)}") from e
