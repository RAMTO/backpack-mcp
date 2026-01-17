"""
Backpack Exchange MCP Server

A Model Context Protocol server that exposes Backpack Exchange API functionality
for order management (list, create, cancel orders), position management (list positions),
and account management (get balances).

Phase 12: Production-ready MCP server with order, position, and balance tools
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from backpack_client import BackpackClient

mcp = FastMCP("Backpack Exchange", json_response=True)
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
        orders = client.get_orders(symbol)
        
        return {
            "orders": orders,
            "count": len(orders),
            "symbol": symbol if symbol else "all"
        }
    except ValueError as e:
        return {
            "error": str(e),
            "orders": [],
            "count": 0,
            "symbol": symbol if symbol else "all"
        }
    except Exception as e:
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
    quantity: Optional[str] = None,
    price: Optional[str] = None,
    timeInForce: str = "GTC",
    quoteQuantity: Optional[str] = None
) -> dict:
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
        Dictionary containing:
        - success: Boolean indicating if order was created
        - order: Order object (if successful), containing:
          * id: New order ID
          * symbol: Trading pair
          * side: "Bid" or "Ask"
          * orderType: "Limit" or "Market"
          * status: Order status
          * quantity: Order quantity
          * price: Limit price (if applicable)
          * timeInForce: Time in force setting
          * createdAt: Timestamp in milliseconds
        - error: Error message (if error occurred)
    """
    try:
        qty = None if quantity is None or quantity == "null" or quantity == "" else quantity
        prc = None if price is None or price == "null" or price == "" else price
        qty_quote = None if quoteQuantity is None or quoteQuantity == "null" or quoteQuantity == "" else quoteQuantity
        
        order = client.create_order(
            symbol=symbol,
            side=side,
            orderType=orderType,
            quantity=qty,
            price=prc,
            timeInForce=timeInForce,
            quoteQuantity=qty_quote
        )
        
        return {
            "success": True,
            "order": order
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "order": None
        }
    except Exception as e:
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
        cancelled_order = client.cancel_order(orderId, symbol)
        
        return {
            "success": True,
            "order": cancelled_order
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "order": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "order": None
        }


@mcp.tool()
def list_positions() -> dict:
    """
    List all open perpetual positions.
    
    Retrieves all open positions for PERP markets. Returns detailed
    information about each position including entry price, mark price,
    PnL, liquidation price, and margin factors.
    
    Returns:
        Dictionary containing:
        - positions: List of position objects, each with:
          * symbol: Trading pair (e.g., "BTC-USDC" or "BTC_USDC_PERP")
          * netQuantity: Net quantity (positive = long, negative = short)
          * entryPrice: Entry price of the position
          * markPrice: Current mark price
          * breakEvenPrice: Break-even price
          * estLiquidationPrice: Estimated liquidation price
          * pnlUnrealized: Unrealized profit/loss
          * pnlRealized: Realized profit/loss
          * netExposureQuantity: Net exposure quantity
          * netExposureNotional: Net exposure notional value
          * positionId: Unique position identifier
          * imf: Initial Margin Factor
          * mmf: Maintenance Margin Factor
          * imfFunction: IMF calculation function details
          * mmfFunction: MMF calculation function details
          * netCost: Net cost of the position
          * cumulativeFundingPayment: Cumulative funding payments
          * cumulativeInterest: Cumulative interest paid/received
          * subaccountId: Subaccount ID
          * userId: User ID
        - count: Number of positions returned
        - error: Error message (if error occurred)
    """
    try:
        positions = client.get_positions()
        
        return {
            "positions": positions,
            "count": len(positions)
        }
    except ValueError as e:
        return {
            "error": str(e),
            "positions": [],
            "count": 0
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "positions": [],
            "count": 0
        }


@mcp.tool()
def get_balances(showZeroBalances: bool = False) -> dict:
    """
    Get all account balances including lent funds.
    
    Retrieves balances for all assets in the account. Returns available,
    locked, staked, and lent amounts for each asset.
    
    This includes funds that are currently lent out (earning interest).
    The total balance for an asset = available + locked + staked + lent.
    
    Args:
        showZeroBalances: If False (default), only show assets with non-zero balances.
                         If True, show all assets including zero balances.
    
    Returns:
        Dictionary containing:
        - balances: Dictionary with asset symbols as keys, each containing:
          * available: Available balance (can be used for trading)
          * locked: Locked balance (committed to open orders)
          * staked: Staked balance (staked for rewards)
          * lent: Lent balance (funds currently lent out, earning interest)
        - count: Number of assets with non-zero balances
        - totalAssets: Total number of assets (including zero balances if showZeroBalances=True)
        - error: Error message (if error occurred)
    """
    try:
        all_balances = client.get_balances()
        
        if showZeroBalances:
            balances = all_balances
        else:
            balances = {}
            for asset, bal in all_balances.items():
                available = float(bal.get('available', '0') or '0')
                locked = float(bal.get('locked', '0') or '0')
                staked = float(bal.get('staked', '0') or '0')
                lent = float(bal.get('lent', '0') or '0')
                
                if available > 0 or locked > 0 or staked > 0 or lent > 0:
                    balances[asset] = bal
        
        return {
            "balances": balances,
            "count": len(balances),
            "totalAssets": len(all_balances)
        }
    except ValueError as e:
        # Return error in response format (don't raise, so MCP can handle it)
        return {
            "error": str(e),
            "balances": {},
            "count": 0,
            "totalAssets": 0
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "balances": {},
            "count": 0,
            "totalAssets": 0
        }


if __name__ == "__main__":
    # Uses stdio transport for local communication (no network exposure)
    mcp.run(transport="stdio")
