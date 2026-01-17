"""
Backpack Exchange API Client

Wrapper around the Backpack API that handles authentication,
HTTP requests, and error handling.

Phase 8: Production-ready client with comprehensive error handling
"""

import requests
import logging
from typing import Optional, List, Dict, Any
from auth import create_auth_from_env

# Set up logging (redact sensitive information)
logger = logging.getLogger(__name__)


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
            # Log request (without sensitive headers)
            logger.debug(f"GET /api/v1/orders with params: {query_params}")
            
            response = requests.get(
                f"{self.base_url}/api/v1/orders",
                params=query_params,
                headers=headers,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Log successful response
            logger.debug(f"GET /api/v1/orders: {response.status_code} - {len(response.json()) if isinstance(response.json(), list) else 1} order(s)")
            
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
            logger.error(f"GET /api/v1/orders network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}") from e
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open perpetual positions.
        
        Retrieves all open positions for PERP markets. Returns positions
        with detailed information including entry price, mark price,
        PnL, liquidation price, and margin factors.
        
        Returns:
            List of position dictionaries, each containing:
            - symbol: Trading pair (e.g., "BTC-USDC" or "BTC_USDC_PERP")
            - netQuantity: Net quantity (positive = long, negative = short)
            - entryPrice: Entry price of the position
            - markPrice: Current mark price
            - breakEvenPrice: Break-even price
            - estLiquidationPrice: Estimated liquidation price
            - pnlUnrealized: Unrealized profit/loss
            - pnlRealized: Realized profit/loss
            - netExposureQuantity: Net exposure quantity
            - netExposureNotional: Net exposure notional value
            - positionId: Unique position identifier
            - imf: Initial Margin Factor
            - mmf: Maintenance Margin Factor
            - imfFunction: IMF calculation function details
            - mmfFunction: MMF calculation function details
            - netCost: Net cost of the position
            - cumulativeFundingPayment: Cumulative funding payments
            - cumulativeInterest: Cumulative interest paid/received
            - subaccountId: Subaccount ID
            - userId: User ID
        
        Raises:
            ValueError: If API returns an error response
            requests.RequestException: If network request fails
        """
        # No query parameters needed - endpoint returns all positions
        # Instruction: 'positionQuery' (following Backpack API pattern)
        headers = self.auth.sign_request(
            instruction='positionQuery',
            params=None,
            window=5000
        )
        
        # Make GET request to retrieve positions
        try:
            # Log request
            logger.debug("GET /api/v1/position")
            
            response = requests.get(
                f"{self.base_url}/api/v1/position",
                headers=headers,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Log successful response
            positions = response.json()
            position_count = len(positions) if isinstance(positions, list) else 1
            logger.debug(f"GET /api/v1/position: {response.status_code} - {position_count} position(s)")
            
            # Parse JSON response
            # API returns a list of positions
            if isinstance(positions, list):
                return positions
            elif isinstance(positions, dict):
                # If API returns a dict, try to extract positions list
                if 'positions' in positions:
                    return positions['positions']
                else:
                    # Return as single-item list if it's a position object
                    return [positions]
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
            logger.error(f"GET /api/v1/position network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}") from e
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel a specific order by ID.
        
        Cancels an order from the order book by its order ID.
        
        Args:
            order_id: The unique identifier of the order to cancel
            symbol: The trading pair symbol (e.g., "BTC_USDC")
        
        Returns:
            Cancelled order dictionary containing:
            - id: Order ID
            - symbol: Trading pair
            - status: Order status (typically "Cancelled")
            - side: "Bid" or "Ask"
            - quantity: Original order quantity
            - price: Limit price (if applicable)
        
        Raises:
            ValueError: If validation fails or API returns an error
            requests.RequestException: If network request fails
        """
        # Validate required parameters
        if not order_id:
            raise ValueError("order_id is required")
        if not symbol:
            raise ValueError("symbol is required")
        
        # Build cancel parameters
        # orderId and symbol are required for cancellation
        cancel_params: Dict[str, str] = {
            'orderId': order_id,
            'symbol': symbol
        }
        
        # Generate signed headers
        # Instruction: 'orderCancel' (from Backpack API docs)
        headers = self.auth.sign_request(
            instruction='orderCancel',
            params=cancel_params,
            window=5000
        )
        
        # Make DELETE request to cancel the order
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/order",
                json=cancel_params,
                headers={
                    **headers,
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            cancelled_order = response.json()
            
            # Return cancellation confirmation
            return cancelled_order
            
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
            logger.error(f"DELETE /api/v1/order network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}") from e
    
    def create_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: Optional[str] = None,
        price: Optional[str] = None,
        timeInForce: str = "GTC",
        quoteQuantity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new order (limit or market).
        
        Places an order on the Backpack Exchange. Supports both limit and market orders.
        Works for both SPOT (e.g., "BTC_USDC") and PERP (e.g., "BTC_USDC_PERP") markets.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC_USDC" for spot, "BTC_USDC_PERP" for perpetual)
            side: Order side - "Bid" (buy) or "Ask" (sell)
            orderType: Order type - "Limit" or "Market"
            quantity: Order quantity (required for limit orders, optional for market if quoteQuantity provided)
            price: Limit price (required for Limit orders, ignored for Market orders)
            timeInForce: Time in force - "GTC" (default), "IOC", or "FOK"
            quoteQuantity: Quote quantity for market orders (e.g., "10" for $10 worth). 
                          For market orders, use either quantity OR quoteQuantity.
        
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
        # Handle None/null values FIRST (from optional parameters or MCP calls)
        # This must happen before any validation
        if quantity is not None and (quantity == "null" or quantity == ""):
            quantity = None
        if quoteQuantity is not None and (quoteQuantity == "null" or quoteQuantity == ""):
            quoteQuantity = None
        if price is not None and (price == "null" or price == ""):
            price = None
        
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
        
        # For market orders: need either quantity or quoteQuantity
        # For limit orders: need quantity
        if orderType == "Market":
            if not quantity and not quoteQuantity:
                raise ValueError("Market orders must specify either 'quantity' or 'quoteQuantity'")
        else:  # Limit order
            if not quantity:
                raise ValueError("quantity is required for Limit orders")
        
        # Validate price for limit orders
        if orderType == "Limit":
            if not price:
                raise ValueError("price is required for Limit orders")
            try:
                float(price)  # Validate it's a number
            except ValueError:
                raise ValueError(f"price must be a valid number, got '{price}'")
        
        # Validate quantity is numeric (if provided)
        if quantity:
            try:
                float(quantity)
            except ValueError:
                raise ValueError(f"quantity must be a valid number, got '{quantity}'")
        
        # Validate quoteQuantity is numeric (if provided)
        if quoteQuantity:
            try:
                float(quoteQuantity)
            except ValueError:
                raise ValueError(f"quoteQuantity must be a valid number, got '{quoteQuantity}'")
        
        # Validate timeInForce
        if timeInForce not in ["GTC", "IOC", "FOK"]:
            raise ValueError(f"timeInForce must be 'GTC', 'IOC', or 'FOK', got '{timeInForce}'")
        
        # Build order parameters
        order_params: Dict[str, str] = {
            'orderType': orderType,
            'side': side,
            'symbol': symbol,
            'timeInForce': timeInForce
        }
        
        # Add quantity or quoteQuantity
        if quantity:
            order_params['quantity'] = quantity
        if quoteQuantity:
            order_params['quoteQuantity'] = quoteQuantity
        
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
            # Log request (without sensitive data)
            safe_params = {k: v for k, v in order_params.items() if k != 'orderId'}
            logger.info(f"POST /api/v1/order: Creating {order_params.get('side')} {order_params.get('orderType')} order for {order_params.get('symbol')}")
            logger.debug(f"POST /api/v1/order params: {safe_params}")
            
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
            
            # Log successful order creation
            logger.info(f"POST /api/v1/order: Order created successfully - ID: {order.get('id')}")
            
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
            logger.error(f"DELETE /api/v1/order network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}") from e
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel a specific order by ID.
        
        Cancels an order from the order book by its order ID.
        
        Args:
            order_id: The unique identifier of the order to cancel
            symbol: The trading pair symbol (e.g., "BTC_USDC")
        
        Returns:
            Cancelled order dictionary containing:
            - id: Order ID
            - symbol: Trading pair
            - status: Order status (typically "Cancelled")
            - side: "Bid" or "Ask"
            - quantity: Original order quantity
            - price: Limit price (if applicable)
        
        Raises:
            ValueError: If validation fails or API returns an error
            requests.RequestException: If network request fails
        """
        # Validate required parameters
        if not order_id:
            raise ValueError("order_id is required")
        if not symbol:
            raise ValueError("symbol is required")
        
        # Build cancel parameters
        # orderId and symbol are required for cancellation
        cancel_params: Dict[str, str] = {
            'orderId': order_id,
            'symbol': symbol
        }
        
        # Generate signed headers
        # Instruction: 'orderCancel' (from Backpack API docs)
        headers = self.auth.sign_request(
            instruction='orderCancel',
            params=cancel_params,
            window=5000
        )
        
        # Make DELETE request to cancel the order
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/order",
                json=cancel_params,
                headers={
                    **headers,
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            cancelled_order = response.json()
            
            # Return cancellation confirmation
            return cancelled_order
            
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
            logger.error(f"DELETE /api/v1/order network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}") from e
