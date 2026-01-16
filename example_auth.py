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
    order_params = {
        'orderType': 'Limit',
        'price': '100.50',
        'quantity': '1.0',
        'side': 'Bid',  # Buy
        'symbol': 'SOL_USDC',
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


def example_cancel_order(order_id: str, symbol: str):
    """Example: Cancel an order."""
    
    auth = create_auth_from_env()
    
    cancel_params = {
        'orderId': order_id,
        'symbol': symbol
    }
    
    headers = auth.sign_request(
        instruction='orderCancel',
        params=cancel_params,
        window=5000
    )
    
    response = requests.delete(
        f"{BASE_URL}/api/v1/order",
        json=cancel_params,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    # example_get_account()
    example_get_balances()
    # example_get_lend_positions()
    # example_place_order()
    pass
