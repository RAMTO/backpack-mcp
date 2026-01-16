"""
Example: Making authenticated requests to Backpack Exchange API

This shows how to use the auth module to make signed API requests.
"""

import os
import requests
from dotenv import load_dotenv
from auth import BackpackAuth, create_auth_from_env

# Load environment variables from .env file
load_dotenv()

# Base URL for Backpack Exchange API
BASE_URL = "https://api.backpack.exchange"


def example_get_account():
    """Example: Get account information (requires auth)."""
    
    try:
        auth = create_auth_from_env()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    headers = auth.sign_request(
        instruction='accountQuery',
        params=None,
        window=5000
    )
    
    response = requests.get(
        f"{BASE_URL}/api/v1/account",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def example_get_balances():
    """Example: Get account balances.
    
    Returns balances for the subaccount associated with your API key.
    Note: Funds that are lent out don't appear here - check borrow/lend positions.
    """
    
    auth = create_auth_from_env()
    
    headers = auth.sign_request(
        instruction='balanceQuery',
        params=None,
        window=5000
    )
    
    response = requests.get(
        f"{BASE_URL}/api/v1/capital",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nBalances:")
        for asset, balance in sorted(result.items()):
            available = float(balance.get('available', '0') or '0')
            locked = float(balance.get('locked', '0') or '0')
            staked = float(balance.get('staked', '0') or '0')
            total = available + locked + staked
            
            if total > 0:
                print(f"  {asset}:")
                print(f"    Available: {balance.get('available', '0')}")
                print(f"    Locked: {balance.get('locked', '0')}")
                print(f"    Staked: {balance.get('staked', '0')}")
    else:
        print(f"Error: {response.text}")


def example_get_lend_positions():
    """Example: Get borrow/lend positions to see lent amounts.
    
    Shows funds that are currently lent out (earning interest).
    These funds don't appear in /api/v1/capital balances.
    """
    
    auth = create_auth_from_env()
    
    headers = auth.sign_request(
        instruction='borrowLendPositionQuery',
        params=None,
        window=5000
    )
    
    response = requests.get(
        f"{BASE_URL}/api/v1/borrowLend/positions",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if len(result) > 0:
            print("\nBorrow/Lend Positions:")
            for pos in result:
                symbol = pos.get('symbol', 'Unknown')
                net_qty = float(pos.get('netQuantity', '0') or '0')
                cumulative_interest = pos.get('cumulativeInterest', '0')
                
                if net_qty > 0:
                    print(f"  {symbol}: Lending {net_qty} (Interest earned: {cumulative_interest})")
                elif net_qty < 0:
                    print(f"  {symbol}: Borrowing {abs(net_qty)} (Interest paid: {cumulative_interest})")
        else:
            print("No active borrow/lend positions")
    else:
        print(f"Error: {response.text}")


def example_place_order():
    """Example: Place a limit order."""
    
    auth = create_auth_from_env()
    
    # Order parameters
    # Buying $10 worth of BTC at $90K limit price
    # Quantity must be a multiple of stepSize (typically 0.001 for BTC)
    # Using 0.001 BTC = $90 worth (closest to $10 that meets precision requirements)
    order_params = {
        'orderType': 'Limit',
        'price': '90000',  # Limit price: $90,000 per BTC
        'quantity': '0.001',  # Amount of BTC to buy (must match stepSize precision, typically 3 decimals)
        'side': 'Bid',  # Buy
        'symbol': 'BTC_USDC',  # BTC/USDC trading pair
        'timeInForce': 'GTC'
    }
    
    # Generate signed headers
    headers = auth.sign_request(
        instruction='orderExecute',
        params=order_params,
        window=5000
    )
    
    # Make the request
    response = requests.post(
        f"{BASE_URL}/api/v1/order",
        json=order_params,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def example_get_open_orders(symbol: str = None):
    """Example: Get all open spot orders.
    
    Retrieves all open orders for SPOT markets.
    
    Reference: GET /api/v1/orders (Backpack Exchange API)
    - Required param: marketType ('SPOT' or 'PERP')
    - Optional param: symbol (to filter by specific trading pair)
    - Instruction: orderQueryAll
    
    Args:
        symbol: Optional. Trading pair symbol (e.g., 'BTC_USDC').
                If None, returns all open spot orders.
    
    Returns:
        List of open orders with details: id, symbol, type, side, 
        status, quantity, price, etc.
    """
    
    auth = create_auth_from_env()
    
    # Build query parameters
    # marketType is REQUIRED - use 'SPOT' for spot orders
    query_params = {
        'marketType': 'SPOT'
    }
    
    # Add optional symbol filter
    if symbol:
        query_params['symbol'] = symbol
    
    # Generate signed headers
    # For GET requests with query params, pass them to sign_request
    # Instruction: 'orderQueryAll' (from Backpack API docs)
    headers = auth.sign_request(
        instruction='orderQueryAll',
        params=query_params,
        window=5000
    )
    
    # Make GET request with query parameters
    response = requests.get(
        f"{BASE_URL}/api/v1/orders",
        params=query_params,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        orders = response.json()
        if len(orders) > 0:
            print(f"\n{'='*60}")
            print(f"Open Spot Orders: {len(orders)} total")
            print(f"{'='*60}")
            
            for i, order in enumerate(orders, 1):
                print(f"\n[{i}] Order ID: {order.get('id', 'N/A')}")
                print(f"    Symbol: {order.get('symbol', 'N/A')}")
                print(f"    Type: {order.get('orderType', 'N/A')}")
                
                side = order.get('side', 'N/A')
                side_label = 'Buy' if side == 'Bid' else 'Sell' if side == 'Ask' else side
                print(f"    Side: {side} ({side_label})")
                
                print(f"    Status: {order.get('status', 'N/A')}")
                print(f"    Quantity: {order.get('quantity', '0')}")
                print(f"    Executed: {order.get('executedQuantity', '0')}")
                
                # Show price if it exists (limit orders)
                price = order.get('price')
                if price:
                    print(f"    Price: {price}")
                
                # Show time in force
                tif = order.get('timeInForce')
                if tif:
                    print(f"    Time In Force: {tif}")
                
                # Show creation time
                created_at = order.get('createdAt')
                if created_at:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(created_at / 1000)
                    print(f"    Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n{'='*60}")
        else:
            print("\nNo open spot orders found")
    else:
        print(f"Error: {response.text}")


def example_cancel_order(order_id: str, symbol: str):
    """Example: Cancel a specific open order.
    
    Cancels an order from the order book by its order ID.
    
    Reference: DELETE /api/v1/order (Backpack Exchange API)
    - Required params: orderId, symbol
    - Instruction: orderCancel
    
    Args:
        order_id: The unique identifier of the order (from example_get_open_orders)
        symbol: The trading pair symbol (e.g., 'BTC_USDC')
    
    Returns:
        Cancellation confirmation with order details
    
    Usage:
        # First, get your open orders to find the order ID
        example_get_open_orders('BTC_USDC')
        
        # Then cancel the specific order
        example_cancel_order('order_12345', 'BTC_USDC')
    """
    
    auth = create_auth_from_env()
    
    # Cancel parameters - orderId and symbol are required
    cancel_params = {
        'orderId': order_id,
        'symbol': symbol
    }
    
    # Generate signed headers with orderCancel instruction
    headers = auth.sign_request(
        instruction='orderCancel',
        params=cancel_params,
        window=5000
    )
    
    # Make DELETE request to cancel the order
    response = requests.delete(
        f"{BASE_URL}/api/v1/order",
        json=cancel_params,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 202]:
        result = response.json()
        print(f"\n✓ Order cancelled successfully!")
        print(f"  Order ID: {result.get('id', order_id)}")
        print(f"  Symbol: {result.get('symbol', symbol)}")
        print(f"  Status: {result.get('status', 'Cancelled')}")
        if result.get('side'):
            side = 'Buy' if result.get('side') == 'Bid' else 'Sell'
            print(f"  Side: {side}")
        if result.get('quantity'):
            print(f"  Quantity: {result.get('quantity')}")
    else:
        print(f"\n✗ Error cancelling order: {response.text}")


def example_cancel_all_orders(symbol: str):
    """Example: Cancel all open orders for a specific symbol.
    
    Cancels all open orders on the specified market at once.
    Useful for quickly closing all positions.
    
    Reference: DELETE /api/v1/orders (Backpack Exchange API)
    - Required param: symbol
    - Instruction: orderCancel
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTC_USDC')
    
    Returns:
        List of cancelled orders
    
    Usage:
        # Cancel all BTC_USDC orders at once
        example_cancel_all_orders('BTC_USDC')
    """
    
    auth = create_auth_from_env()
    
    # Cancel parameters - symbol is required
    cancel_params = {
        'symbol': symbol
    }
    
    # Generate signed headers with orderCancel instruction
    headers = auth.sign_request(
        instruction='orderCancel',
        params=cancel_params,
        window=5000
    )
    
    # Make DELETE request to cancel all orders
    response = requests.delete(
        f"{BASE_URL}/api/v1/orders",
        json=cancel_params,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 202]:
        cancelled_orders = response.json()
        if isinstance(cancelled_orders, list) and len(cancelled_orders) > 0:
            print(f"\n✓ Cancelled {len(cancelled_orders)} order(s):")
            for i, order in enumerate(cancelled_orders, 1):
                side = 'Buy' if order.get('side') == 'Bid' else 'Sell'
                print(f"  [{i}] {order.get('id')} | {side} {order.get('quantity')} @ {order.get('price', 'Market')}")
        elif isinstance(cancelled_orders, list):
            print("\nNo orders to cancel")
        else:
            print(f"\n✓ Orders cancelled: {cancelled_orders}")
    else:
        print(f"\n✗ Error cancelling orders: {response.text}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    # Account & Balance queries
    # example_get_account()
    # example_get_balances()
    # example_get_lend_positions()
    
    # Trading
    # example_place_order()
    
    # View open orders
    # example_get_open_orders()  # All open spot orders
    # example_get_open_orders('BTC_USDC')  # Only BTC_USDC orders
    
    # Cancel orders
    # Step 1: Get order ID from example_get_open_orders() above
    # Step 2: Cancel specific order:
    # example_cancel_order('27586447764', 'BTC_USDC')
    
    # Or cancel all orders for a symbol at once:
    # example_cancel_all_orders('BTC_USDC')
    
    pass
