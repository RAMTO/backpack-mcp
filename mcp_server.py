"""
Backpack Exchange MCP Server

A Model Context Protocol server that exposes Backpack Exchange API functionality
for order management (list, create, cancel orders).

Phase 8: Production-ready MCP server with all tools and comprehensive error handling
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from backpack_client import BackpackClient

# Create FastMCP server instance
# json_response=True ensures responses are in JSON format
mcp = FastMCP("Backpack Exchange", json_response=True)

# Initialize Backpack client
# This will load API keys from environment variables
client = BackpackClient()


@mcp.tool()
def list_orders(symbol: Optional[str] = None) -> dict:
    """
    List all open spot orders, optionally filtered by symbol.
    
    Retrieves all open orders for SPOT markets. If symbol is provided,
    only returns orders for that trading pair.
    
    Args:
        symbol: Optional trading pair symbol (e.g., "BTC_USDC").
               If None, returns all open spot orders.
    
    Returns:
        Dictionary containing:
        - orders: List of order objects, each with:
          * id: Order ID
          * symbol: Trading pair
          * side: "Bid" (buy) or "Ask" (sell)
          * orderType: "Limit", "Market", etc.
          * status: Order status
          * quantity: Order quantity
          * executedQuantity: Filled quantity
          * price: Limit price (if applicable)
          * timeInForce: "GTC", "IOC", etc.
          * createdAt: Timestamp in milliseconds
        - count: Number of orders returned
        - symbol: Filter symbol used (if any)
    
    Raises:
        ValueError: If API returns an error (wrapped in response dict)
    """
    try:
        # Call the Backpack client to get orders
        orders = client.get_orders(symbol)
        
        # Return structured response
        return {
            "orders": orders,
            "count": len(orders),
            "symbol": symbol if symbol else "all"
        }
    except ValueError as e:
        # Return error in response format (don't raise, so MCP can handle it)
        return {
            "error": str(e),
            "orders": [],
            "count": 0,
            "symbol": symbol if symbol else "all"
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "error": f"Unexpected error: {str(e)}",
            "orders": [],
            "count": 0,
            "symbol": symbol if symbol else "all"
        }


@mcp.tool()
def create_order(
    symbol: str,
    side: str,
    orderType: str,
    quantity: str,
    price: Optional[str] = None,
    timeInForce: str = "GTC"
) -> dict:
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
        Dictionary containing:
        - id: New order ID
        - symbol: Trading pair
        - side: "Bid" or "Ask"
        - orderType: "Limit" or "Market"
        - status: Order status
        - quantity: Order quantity
        - price: Limit price (if applicable)
        - timeInForce: Time in force setting
        - createdAt: Timestamp in milliseconds
        - error: Error message (if error occurred)
    """
    try:
        # Call the Backpack client to create the order
        order = client.create_order(
            symbol=symbol,
            side=side,
            orderType=orderType,
            quantity=quantity,
            price=price,
            timeInForce=timeInForce
        )
        
        # Return order confirmation
        return {
            "success": True,
            "order": order
        }
    except ValueError as e:
        # Return error in response format (don't raise, so MCP can handle it)
        return {
            "success": False,
            "error": str(e),
            "order": None
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "order": None
        }


@mcp.tool()
def cancel_order(orderId: str, symbol: str) -> dict:
    """
    Cancel a specific order by ID.
    
    Cancels an order from the order book by its order ID.
    
    Args:
        orderId: The unique identifier of the order to cancel
        symbol: The trading pair symbol (e.g., "BTC_USDC")
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if cancellation was successful
        - order: Cancelled order object (if successful), containing:
          * id: Order ID
          * symbol: Trading pair
          * status: Order status (typically "Cancelled")
          * side: "Bid" or "Ask"
          * quantity: Original order quantity
          * price: Limit price (if applicable)
        - error: Error message (if error occurred)
    """
    try:
        # Call the Backpack client to cancel the order
        cancelled_order = client.cancel_order(orderId, symbol)
        
        # Return cancellation confirmation
        return {
            "success": True,
            "order": cancelled_order
        }
    except ValueError as e:
        # Return error in response format (don't raise, so MCP can handle it)
        return {
            "success": False,
            "error": str(e),
            "order": None
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "order": None
        }


if __name__ == "__main__":
    # Run the server using stdio transport
    # This allows local communication via stdin/stdout
    # No network exposure - safe for local usage
    mcp.run(transport="stdio")
