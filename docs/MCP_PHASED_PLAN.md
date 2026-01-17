# Backpack MCP Server - Phased Implementation Plan

## Overview
Break down implementation into testable phases. Each phase can be completed and verified before moving to the next.

---

## Phase 0: Setup & Dependencies ✅
**Goal**: Install dependencies and verify environment

**Tasks**:
1. Install MCP SDK: `pip install "mcp[cli]"`
2. Verify existing dependencies: `requests`, `python-dotenv`, `cryptography`
3. Update `requirements.txt` with `mcp[cli]`
4. Verify `.env` file exists with keys

**Test**:
```bash
# Verify imports work
python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
python -c "from auth import create_auth_from_env; print('OK')"
```

**Success Criteria**: ✅ All imports succeed, no errors

---

## Phase 1: Minimal MCP Server (Hello World)
**Goal**: Create a working MCP server with one dummy tool

**Deliverable**: `mcp_server.py` with a simple test tool

**Implementation**:
- Create basic FastMCP server
- Add one dummy tool (e.g., `hello_world()`)
- Use stdio transport
- No Backpack API calls yet

**Code Structure**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Backpack Exchange")

@mcp.tool()
def hello_world(name: str = "World") -> dict:
    """A simple test tool."""
    return {"message": f"Hello, {name}!"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Test**:
1. **Manual test with MCP Inspector** (if available):
   ```bash
   # Run server and check it starts
   python mcp_server.py
   ```

2. **Test with MCP client tool**:
   ```bash
   # Use mcp CLI to list tools
   mcp list-tools --server python mcp_server.py
   ```

3. **Test tool call** (if MCP client available):
   ```bash
   # Call the hello_world tool
   mcp call-tool --server python mcp_server.py --tool hello_world --args '{"name": "Test"}'
   ```

**Alternative Test** (if MCP tools not available):
- Create a simple test script that imports and calls the tool directly:
  ```python
  from mcp_server import hello_world
  result = hello_world("Test")
  assert result["message"] == "Hello, Test!"
  print("✅ Phase 1 test passed")
  ```

**Success Criteria**: ✅ 
- Server starts without errors
- Tool is registered and callable
- Returns expected response

---

## Phase 2: Backpack Client - Get Orders
**Goal**: Create client wrapper with one working method

**Deliverable**: `backpack_client.py` with `get_orders()` method

**Implementation**:
- Create `BackpackClient` class
- Initialize with `BackpackAuth` from env
- Implement `get_orders(symbol=None)` method
- Handle errors and return clean data
- Reuse logic from `example_get_open_orders()`

**Code Structure**:
```python
from auth import create_auth_from_env
import requests

class BackpackClient:
    def __init__(self):
        self.auth = create_auth_from_env()
        self.base_url = "https://api.backpack.exchange"
    
    def get_orders(self, symbol: str | None = None) -> dict:
        """Get open spot orders."""
        # Implementation here
```

**Test**:
```python
# test_client.py
from backpack_client import BackpackClient

client = BackpackClient()

# Test 1: Get all orders
print("Test 1: Get all orders...")
result = client.get_orders()
print(f"✅ Got {len(result)} orders")
print(f"Sample: {result[0] if result else 'No orders'}")

# Test 2: Get orders for specific symbol
print("\nTest 2: Get BTC_USDC orders...")
result = client.get_orders("BTC_USDC")
print(f"✅ Got {len(result)} orders for BTC_USDC")

# Test 3: Error handling (invalid symbol)
print("\nTest 3: Error handling...")
try:
    result = client.get_orders("INVALID_SYMBOL")
    print(f"Result: {result}")
except Exception as e:
    print(f"✅ Error handled: {type(e).__name__}")
```

**Success Criteria**: ✅
- Client initializes successfully
- `get_orders()` returns list of orders (or empty list)
- Works with and without symbol filter
- Errors are handled gracefully

---

## Phase 3: MCP Tool - List Orders
**Goal**: Connect MCP server to Backpack client for listing orders

**Deliverable**: Working `list_orders` tool in MCP server

**Implementation**:
- Import `BackpackClient` in `mcp_server.py`
- Add `list_orders` tool that calls `client.get_orders()`
- Handle errors and return proper format

**Code Addition**:
```python
from backpack_client import BackpackClient

client = BackpackClient()

@mcp.tool()
def list_orders(symbol: str | None = None) -> dict:
    """List all open spot orders, optionally filtered by symbol."""
    try:
        orders = client.get_orders(symbol)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        return {"error": str(e)}
```

**Test**:
1. **Direct function test**:
   ```python
   # test_mcp_tool.py
   from mcp_server import list_orders
   
   result = list_orders()
   print(f"✅ Got {result['count']} orders")
   
   result = list_orders("BTC_USDC")
   print(f"✅ Got {result['count']} BTC_USDC orders")
   ```

2. **MCP protocol test** (if tools available):
   - Use MCP client to call `list_orders` tool
   - Verify JSON-RPC response format

**Success Criteria**: ✅
- Tool is registered in MCP server
- Returns orders in correct format
- Handles errors properly
- Works with optional symbol parameter

---

## Phase 4: Backpack Client - Create Order
**Goal**: Add order creation to client

**Deliverable**: `create_order()` method in `BackpackClient`

**Implementation**:
- Add `create_order()` method
- Validate required parameters
- Handle Limit vs Market order differences
- Reuse logic from `example_place_order()`

**Test**:
```python
# test_create_order.py
from backpack_client import BackpackClient

client = BackpackClient()

# Test 1: Create limit order (use small amount for testing!)
print("Test 1: Create limit order...")
result = client.create_order(
    symbol="BTC_USDC",
    side="Bid",
    orderType="Limit",
    quantity="0.001",
    price="50000",  # Use a price that won't execute immediately
    timeInForce="GTC"
)
print(f"✅ Order created: {result.get('id')}")

# Test 2: Validation (missing price for limit order)
print("\nTest 2: Validation test...")
try:
    result = client.create_order(
        symbol="BTC_USDC",
        side="Bid",
        orderType="Limit",
        quantity="0.001"
        # Missing price - should fail
    )
    print("❌ Should have failed")
except ValueError as e:
    print(f"✅ Validation works: {e}")
```

**Success Criteria**: ✅
- Creates orders successfully
- Validates required parameters
- Returns order confirmation
- Handles API errors

---

## Phase 5: MCP Tool - Create Order
**Goal**: Expose order creation as MCP tool

**Deliverable**: Working `create_order` tool

**Implementation**:
- Add `create_order` tool to MCP server
- Map MCP tool parameters to client method
- Add input validation

**Test**:
```python
# test_create_tool.py
from mcp_server import create_order

result = create_order(
    symbol="BTC_USDC",
    side="Bid",
    orderType="Limit",
    quantity="0.001",
    price="50000"
)
print(f"✅ Order created via MCP: {result.get('id')}")
```

**Success Criteria**: ✅
- Tool creates orders via MCP
- Parameters are validated
- Returns proper response format

---

## Phase 6: Backpack Client - Cancel Order
**Goal**: Add order cancellation to client

**Deliverable**: `cancel_order()` method

**Implementation**:
- Add `cancel_order(order_id, symbol)` method
- Reuse logic from `example_cancel_order()`

**Test**:
```python
# test_cancel_order.py
from backpack_client import BackpackClient

client = BackpackClient()

# First, get an order ID from list_orders
orders = client.get_orders("BTC_USDC")
if orders:
    order_id = orders[0]["id"]
    symbol = orders[0]["symbol"]
    
    print(f"Test: Cancel order {order_id}...")
    result = client.cancel_order(order_id, symbol)
    print(f"✅ Order cancelled: {result.get('status')}")
else:
    print("No orders to cancel for testing")
```

**Success Criteria**: ✅
- Cancels orders successfully
- Handles invalid order IDs
- Returns cancellation confirmation

---

## Phase 7: MCP Tool - Cancel Order
**Goal**: Expose order cancellation as MCP tool

**Deliverable**: Working `cancel_order` tool

**Test**:
```python
# test_cancel_tool.py
from mcp_server import cancel_order

# Use a real order ID from your account
result = cancel_order(orderId="12345", symbol="BTC_USDC")
print(f"✅ Order cancelled via MCP: {result.get('status')}")
```

**Success Criteria**: ✅
- Tool cancels orders via MCP
- Works with real order IDs

---

## Phase 8: Integration Testing & Polish
**Goal**: Test all tools together and add error handling

**Tasks**:
1. Test all three tools end-to-end
2. Add comprehensive error handling
3. Add input validation
4. Add logging (with sensitive data redacted)
5. Test error cases (invalid params, network errors, etc.)

**Test Scenarios**:
```python
# test_integration.py
from mcp_server import list_orders, create_order, cancel_order

# Scenario 1: Full workflow
print("Scenario 1: Create → List → Cancel")
order = create_order(
    symbol="BTC_USDC",
    side="Bid",
    orderType="Limit",
    quantity="0.001",
    price="50000"
)
order_id = order["id"]

orders = list_orders("BTC_USDC")
assert any(o["id"] == order_id for o in orders["orders"])

result = cancel_order(orderId=order_id, symbol="BTC_USDC")
assert result["status"] == "Cancelled"
print("✅ Full workflow works")

# Scenario 2: Error handling
print("\nScenario 2: Error handling")
try:
    cancel_order(orderId="invalid", symbol="BTC_USDC")
except Exception as e:
    print(f"✅ Error handled: {type(e).__name__}")
```

**Success Criteria**: ✅
- All tools work together
- Errors are handled gracefully
- Input validation works
- Ready for production use

---

## Phase 9: Backpack Client - Get Positions
**Goal**: Add method to retrieve perpetual positions

**Deliverable**: `get_positions()` method in `BackpackClient`

**Implementation**:
- Add `get_positions()` method to `BackpackClient`
- Call `GET /api/v1/position` endpoint
- Use `positionQuery` instruction (or test `positionQueryAll` if needed)
- Handle errors and return clean data
- No query parameters needed (returns all positions)

**Code Structure**:
```python
def get_positions(self) -> List[Dict[str, Any]]:
    """
    Get all open perpetual positions.
    
    Retrieves all open positions for PERP markets.
    Returns positions with details like entry price, mark price,
    PnL, liquidation price, etc.
    
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
        - cumulativeFundingPayment: Cumulative funding payments
        - subaccountId: Subaccount ID
        - userId: User ID
    """
    # Implementation here
```

**Test**:
```python
# test_positions.py
from backpack_client import BackpackClient

client = BackpackClient()

# Test 1: Get all positions
print("Test 1: Get all positions...")
result = client.get_positions()
print(f"✅ Got {len(result)} positions")
if result:
    pos = result[0]
    print(f"Sample position:")
    print(f"  Symbol: {pos.get('symbol')}")
    print(f"  Net Quantity: {pos.get('netQuantity')}")
    print(f"  Entry Price: {pos.get('entryPrice')}")
    print(f"  Mark Price: {pos.get('markPrice')}")
    print(f"  Unrealized PnL: {pos.get('pnlUnrealized')}")
else:
    print("No open positions")

# Test 2: Error handling
print("\nTest 2: Error handling...")
# Test with invalid auth or network error scenarios
```

**Success Criteria**: ✅
- Client method initializes successfully
- `get_positions()` returns list of positions (or empty list)
- Returns all expected position fields
- Errors are handled gracefully
- Works with accounts that have no positions (returns empty list)

---

## Phase 10: MCP Tool - List Positions
**Goal**: Connect MCP server to Backpack client for listing positions

**Deliverable**: Working `list_positions` tool in MCP server

**Implementation**:
- Add `list_positions` tool to `mcp_server.py`
- Call `client.get_positions()`
- Handle errors and return proper format
- Return structured response with position details

**Code Addition**:
```python
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
          * symbol: Trading pair
          * netQuantity: Net quantity (positive = long, negative = short)
          * entryPrice: Entry price
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
          * cumulativeFundingPayment: Cumulative funding payments
          * subaccountId: Subaccount ID
          * userId: User ID
        - count: Number of positions returned
    """
    try:
        positions = client.get_positions()
        return {
            "positions": positions,
            "count": len(positions)
        }
    except Exception as e:
        return {
            "error": str(e),
            "positions": [],
            "count": 0
        }
```

**Test**:
1. **Direct function test**:
   ```python
   # test_list_positions_tool.py
   from mcp_server import list_positions
   
   result = list_positions()
   print(f"✅ Got {result['count']} positions")
   
   if result['count'] > 0:
       pos = result['positions'][0]
       print(f"Sample position: {pos.get('symbol')} - {pos.get('netQuantity')}")
   ```

2. **MCP protocol test** (if tools available):
   - Use MCP client to call `list_positions` tool
   - Verify JSON-RPC response format
   - Check position data structure

**Success Criteria**: ✅
- Tool is registered in MCP server
- Returns positions in correct format
- Handles errors properly
- Returns empty list when no positions exist
- All position fields are included in response

---

## Phase 11: Backpack Client - Get Balances
**Goal**: Add method to retrieve account balances

**Deliverable**: `get_balances()` method in `BackpackClient`

**Implementation**:
- Add `get_balances()` method to `BackpackClient`
- Call `GET /api/v1/capital` endpoint
- Use `balanceQuery` instruction (from Backpack API docs)
- No query parameters needed (returns all balances)
- Handle errors and return clean data
- Reuse logic from `example_get_balances()`

**Code Structure**:
```python
def get_balances(self) -> Dict[str, Dict[str, str]]:
    """
    Get all account balances.
    
    Retrieves balances for all assets in the account. Returns available,
    locked, and staked amounts for each asset.
    
    Note: Funds that are lent out don't appear here - check borrow/lend positions.
    
    Returns:
        Dictionary with asset symbols as keys, each containing:
        - available: Available balance (can be used for trading)
        - locked: Locked balance (committed to open orders)
        - staked: Staked balance (staked for rewards)
        
        Example:
        {
            "BTC": {
                "available": "0.5",
                "locked": "0.1",
                "staked": "0.0"
            },
            "USDC": {
                "available": "1000.0",
                "locked": "50.0",
                "staked": "0.0"
            }
        }
    
    Raises:
        ValueError: If API returns an error response
        requests.RequestException: If network request fails
    """
    # Implementation here
```

**Test**:
```python
# test_balances.py
from backpack_client import BackpackClient

client = BackpackClient()

# Test 1: Get all balances
print("Test 1: Get all balances...")
result = client.get_balances()
print(f"✅ Got balances for {len(result)} assets")

if result:
    # Show first few assets with non-zero balances
    print("\nSample balances:")
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
            print(f"    Total: {total}")
            break  # Show first non-zero balance
else:
    print("No balances found")

# Test 2: Error handling
print("\nTest 2: Error handling...")
# Test with invalid auth or network error scenarios
```

**Success Criteria**: ✅
- Client method initializes successfully
- `get_balances()` returns dictionary of balances
- Returns all expected balance fields (available, locked, staked)
- Handles assets with zero balances correctly
- Errors are handled gracefully
- Works with accounts that have no balances (returns empty dict)

---

## Phase 12: MCP Tool - Get Balances
**Goal**: Connect MCP server to Backpack client for retrieving balances

**Deliverable**: Working `get_balances` tool in MCP server

**Implementation**:
- Add `get_balances` tool to `mcp_server.py`
- Call `client.get_balances()`
- Handle errors and return proper format
- Return structured response with balance details
- Optionally filter to show only assets with non-zero balances

**Code Addition**:
```python
@mcp.tool()
def get_balances(showZeroBalances: bool = False) -> dict:
    """
    Get all account balances.
    
    Retrieves balances for all assets in the account. Returns available,
    locked, and staked amounts for each asset.
    
    Note: Funds that are lent out don't appear here - check borrow/lend positions.
    
    Args:
        showZeroBalances: If False (default), only show assets with non-zero balances.
                         If True, show all assets including zero balances.
    
    Returns:
        Dictionary containing:
        - balances: Dictionary with asset symbols as keys, each containing:
          * available: Available balance (can be used for trading)
          * locked: Locked balance (committed to open orders)
          * staked: Staked balance (staked for rewards)
        - count: Number of assets with balances
        - totalAssets: Total number of assets (including zero balances if showZeroBalances=True)
        - error: Error message (if error occurred)
    """
    try:
        # Call the Backpack client to get balances
        all_balances = client.get_balances()
        
        # Filter zero balances if requested
        if showZeroBalances:
            balances = all_balances
        else:
            balances = {
                asset: bal for asset, bal in all_balances.items()
                if float(bal.get('available', '0') or '0') > 0
                or float(bal.get('locked', '0') or '0') > 0
                or float(bal.get('staked', '0') or '0') > 0
            }
        
        # Return structured response
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
        # Handle unexpected errors
        return {
            "error": f"Unexpected error: {str(e)}",
            "balances": {},
            "count": 0,
            "totalAssets": 0
        }
```

**Test**:
1. **Direct function test**:
   ```python
   # test_get_balances_tool.py
   from mcp_server import get_balances
   
   result = get_balances()
   print(f"✅ Got balances for {result['count']} assets")
   
   if result['count'] > 0:
       # Show first asset
       asset = list(result['balances'].keys())[0]
       bal = result['balances'][asset]
       print(f"Sample: {asset} - Available: {bal.get('available')}")
   ```

2. **MCP protocol test** (if tools available):
   - Use MCP client to call `get_balances` tool
   - Verify JSON-RPC response format
   - Check balance data structure
   - Test with `showZeroBalances=True` and `False`

**Success Criteria**: ✅
- Tool is registered in MCP server
- Returns balances in correct format
- Handles errors properly
- Filters zero balances correctly when requested
- All balance fields are included in response
- Works with accounts that have no balances (returns empty dict)

---

## Testing Strategy Summary

### Unit Tests (Per Phase)
- Test each component in isolation
- Mock dependencies where needed
- Test error cases

### Integration Tests (Phase 8)
- Test tools together
- Test with real API (carefully!)
- Test error scenarios

### Manual Testing
- Use MCP client tools if available
- Test via AI assistant integration
- Verify responses are correct

---

## Phase Dependencies

```
Phase 0 (Setup)
    ↓
Phase 1 (Minimal MCP Server)
    ↓
Phase 2 (Client - Get Orders)
    ↓
Phase 3 (MCP Tool - List Orders) ✅ Can test end-to-end here
    ↓
Phase 4 (Client - Create Order)
    ↓
Phase 5 (MCP Tool - Create Order) ✅ Can test end-to-end here
    ↓
Phase 6 (Client - Cancel Order)
    ↓
Phase 7 (MCP Tool - Cancel Order) ✅ Can test end-to-end here
    ↓
Phase 8 (Integration & Polish)
    ↓
Phase 9 (Client - Get Positions)
    ↓
Phase 10 (MCP Tool - List Positions) ✅ Can test end-to-end here
    ↓
Phase 11 (Client - Get Balances)
    ↓
Phase 12 (MCP Tool - Get Balances) ✅ Can test end-to-end here
```

---

## Success Milestones

- ✅ **Phase 1**: MCP server works (hello world)
- ✅ **Phase 3**: Can list orders via MCP
- ✅ **Phase 5**: Can create orders via MCP
- ✅ **Phase 7**: Can cancel orders via MCP
- ✅ **Phase 8**: Production-ready MCP server (orders)
- ⬜ **Phase 9**: Can retrieve positions via client
- ⬜ **Phase 10**: Can list positions via MCP
- ⬜ **Phase 11**: Can retrieve balances via client
- ⬜ **Phase 12**: Can get balances via MCP

Each phase builds on the previous but can be tested independently!
