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
    
    def create_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: str,
        price: Optional[str] = None,
        timeInForce: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Create a new order (limit or market).
        
        Places an order on the Backpack Exchange. Supports both limit and market orders.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC_USDC")
            side: Order side - "Bid" (buy) or "Ask" (sell)
            orderType: Order type - "Limit" or "Market"
            quantity: Order quantity (must match stepSize precision for the symbol)
            price: Limit price (required for Limit orders, ignored for Market orders)
            timeInForce: Time in force - "GTC" (default), "IOC", or "FOK"
        
        Returns:
            Order dictionary containing:
            - id: New order ID
            - symbol: Trading pair
            - side: "Bid" or "Ask"
            - orderType: "Limit" or "Market"
            - status: Order status
            - quantity: Order quantity
            - price: Limit price (if applicable)
            - timeInForce: Time in force setting
            - createdAt: Timestamp in milliseconds
        
        Raises:
            ValueError: If validation fails or API returns an error
            requests.RequestException: If network request fails
        """
        # Validate required parameters
        if not symbol:
            raise ValueError("symbol is required")
        if not side:
            raise ValueError("side is required")
        if side not in ["Bid", "Ask"]:
            raise ValueError(f"side must be 'Bid' or 'Ask', got '{side}'")
        if not orderType:
            raise ValueError("orderType is required")
        if orderType not in ["Limit", "Market"]:
            raise ValueError(f"orderType must be 'Limit' or 'Market', got '{orderType}'")
        if not quantity:
            raise ValueError("quantity is required")
        
        # Validate price for limit orders
        if orderType == "Limit":
            if not price:
                raise ValueError("price is required for Limit orders")
            try:
                float(price)  # Validate it's a number
            except ValueError:
                raise ValueError(f"price must be a valid number, got '{price}'")
        
        # Validate quantity is numeric
        try:
            float(quantity)
        except ValueError:
            raise ValueError(f"quantity must be a valid number, got '{quantity}'")
        
        # Validate timeInForce
        if timeInForce not in ["GTC", "IOC", "FOK"]:
            raise ValueError(f"timeInForce must be 'GTC', 'IOC', or 'FOK', got '{timeInForce}'")
        
        # Build order parameters
        order_params: Dict[str, str] = {
            'orderType': orderType,
            'quantity': quantity,
            'side': side,
            'symbol': symbol,
            'timeInForce': timeInForce
        }
        
        # Add price for limit orders
        if orderType == "Limit" and price:
            order_params['price'] = price
        
        # Generate signed headers
        # Instruction: 'orderExecute' (from Backpack API docs)
        headers = self.auth.sign_request(
            instruction='orderExecute',
            params=order_params,
            window=5000
        )
        
        # Make POST request to create the order
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/order",
                json=order_params,
                headers={
                    **headers,
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            order = response.json()
            
            # Return order confirmation
            return order
            
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
