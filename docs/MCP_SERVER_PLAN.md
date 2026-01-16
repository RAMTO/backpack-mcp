# Backpack MCP Server - Implementation Plan

## Overview
Create a local-only MCP server that exposes Backpack Exchange API functionality for order management (view, create, cancel orders).

## Architecture

### Components
1. **MCP Server** (`mcp_server.py`) - Main FastMCP server implementation
2. **Backpack Client** (`backpack_client.py`) - Wrapper around existing `auth.py` for API calls
3. **Configuration** - Environment variables for API keys (reuse existing `.env`)

## MCP Tools (Functions)

### 1. `list_orders`
**Purpose**: Show all open spot orders

**Parameters**:
- `symbol` (optional, string): Filter by trading pair (e.g., "BTC_USDC")
  - If not provided, returns all open orders

**Returns**: JSON array of order objects with:
- `id`: Order ID
- `symbol`: Trading pair
- `side`: "Bid" (buy) or "Ask" (sell)
- `orderType`: "Limit", "Market", etc.
- `status`: Order status
- `quantity`: Order quantity
- `executedQuantity`: Filled quantity
- `price`: Limit price (if applicable)
- `timeInForce`: "GTC", "IOC", etc.
- `createdAt`: Timestamp

**Implementation**:
- Uses `orderQueryAll` instruction
- GET `/api/v1/orders?marketType=SPOT&symbol={symbol}`
- Reuses `example_get_open_orders()` logic

---

### 2. `create_order`
**Purpose**: Place a new order (limit or market)

**Parameters**:
- `symbol` (required, string): Trading pair (e.g., "BTC_USDC")
- `side` (required, string): "Bid" (buy) or "Ask" (sell)
- `orderType` (required, string): "Limit" or "Market"
- `quantity` (required, string): Order quantity (must match stepSize precision)
- `price` (optional, string): Limit price (required for Limit orders)
- `timeInForce` (optional, string): "GTC", "IOC", "FOK" (default: "GTC")

**Returns**: Order object with confirmation:
- `id`: New order ID
- `symbol`: Trading pair
- `status`: Order status
- `quantity`: Order quantity
- `price`: Limit price (if applicable)

**Validation**:
- Validate `orderType` is "Limit" or "Market"
- Validate `side` is "Bid" or "Ask"
- If `orderType` is "Limit", require `price`
- Validate `quantity` format (numeric string)

**Implementation**:
- Uses `orderExecute` instruction
- POST `/api/v1/order` with JSON body
- Reuses `example_place_order()` logic

---

### 3. `cancel_order`
**Purpose**: Cancel a specific order by ID

**Parameters**:
- `orderId` (required, string): Order ID to cancel
- `symbol` (required, string): Trading pair (e.g., "BTC_USDC")

**Returns**: Cancelled order object:
- `id`: Order ID
- `symbol`: Trading pair
- `status`: "Cancelled"
- `quantity`: Original quantity

**Implementation**:
- Uses `orderCancel` instruction
- DELETE `/api/v1/order` with JSON body `{orderId, symbol}`
- Reuses `example_cancel_order()` logic

---

### 4. `cancel_all_orders` (Optional Enhancement)
**Purpose**: Cancel all orders for a symbol

**Parameters**:
- `symbol` (required, string): Trading pair

**Returns**: Array of cancelled orders

**Implementation**:
- Uses `orderCancel` instruction
- DELETE `/api/v1/orders` with JSON body `{symbol}`
- Reuses `example_cancel_all_orders()` logic

## MCP Resources (Optional - for context)

### 1. `backpack://account`
**Purpose**: Get account information

**Returns**: Account details (subaccount info, etc.)

### 2. `backpack://balance/{asset}`
**Purpose**: Get balance for specific asset

**Returns**: Available, locked, staked amounts

## Implementation Steps

### Step 1: Setup Dependencies
```bash
pip install "mcp[cli]" requests
```
- `mcp` - Official MCP Python SDK
- `requests` - Already in requirements, but verify

### Step 2: Create Backpack Client Wrapper
**File**: `backpack_client.py`

**Purpose**: Encapsulate API calls and error handling

**Functions**:
- `__init__()`: Initialize with `BackpackAuth` from env
- `get_orders(symbol=None)`: Fetch open orders
- `create_order(params)`: Place new order
- `cancel_order(order_id, symbol)`: Cancel specific order
- `cancel_all_orders(symbol)`: Cancel all for symbol

**Error Handling**:
- Wrap API calls in try/except
- Return structured error responses
- Handle HTTP errors (400, 401, 500, etc.)

### Step 3: Create MCP Server
**File**: `mcp_server.py`

**Structure**:
```python
from mcp.server.fastmcp import FastMCP
from backpack_client import BackpackClient

mcp = FastMCP("Backpack Exchange", json_response=True)
client = BackpackClient()

@mcp.tool()
def list_orders(symbol: str | None = None) -> dict:
    """List all open spot orders, optionally filtered by symbol."""
    # Implementation
    
@mcp.tool()
def create_order(
    symbol: str,
    side: str,
    orderType: str,
    quantity: str,
    price: str | None = None,
    timeInForce: str = "GTC"
) -> dict:
    """Create a new order (limit or market)."""
    # Implementation
    
@mcp.tool()
def cancel_order(orderId: str, symbol: str) -> dict:
    """Cancel a specific order by ID."""
    # Implementation

if __name__ == "__main__":
    mcp.run(transport="stdio")  # Local usage via stdin/stdout
```

### Step 4: Add Type Hints & Validation
- Use Pydantic models for request/response validation (optional)
- Add type hints for all tool parameters
- Validate enum values (side, orderType, timeInForce)

### Step 5: Error Handling & Logging
- Log all API calls (with sensitive data redacted)
- Return user-friendly error messages
- Handle network errors gracefully
- Validate inputs before API calls

### Step 6: Testing
- Test each tool individually
- Test error cases (invalid order ID, missing params, etc.)
- Test with real API (use testnet if available)

### Step 7: Configuration
**File**: `.env` (already exists)
- `BACKPACK_PRIVATE_KEY` or `BACKPACK_SECRET_KEY`
- `BACKPACK_PUBLIC_KEY` or `BACKPACK_API_KEY`

**Optional Config**:
- `BACKPACK_BASE_URL` (default: "https://api.backpack.exchange")
- `BACKPACK_TIMEOUT` (default: 30 seconds)

## Security Considerations (Local Usage)

1. **No Network Exposure**: Use `stdio` transport (not HTTP)
   - Server only communicates via stdin/stdout
   - No external network access

2. **Environment Variables**: 
   - Keys stored in `.env` file (already in `.gitignore`)
   - Never log or expose private keys

3. **Input Validation**:
   - Validate all user inputs
   - Prevent injection attacks (though less relevant for local MCP)

4. **Error Messages**:
   - Don't expose sensitive info in error messages
   - Sanitize API error responses

## File Structure

```
backpack-api/
├── auth.py                    # Existing (keep)
├── example_auth.py            # Existing (keep)
├── backpack_client.py         # NEW - API client wrapper
├── mcp_server.py              # NEW - MCP server implementation
├── requirements.txt           # Update with mcp dependency
├── .env                       # Existing (keep)
└── MCP_SERVER_PLAN.md         # This file
```

## Usage Example

Once implemented, the MCP server can be used by AI assistants via:

```json
{
  "mcpServers": {
    "backpack": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

The AI can then call:
- "List my open orders"
- "Create a limit buy order for 0.001 BTC at $90,000"
- "Cancel order 12345 for BTC_USDC"

## Next Steps

1. ✅ Create plan (this document)
2. ⬜ Create `backpack_client.py` wrapper
3. ⬜ Create `mcp_server.py` with FastMCP
4. ⬜ Add error handling and validation
5. ⬜ Test with real API
6. ⬜ Document usage in README

## Open Questions

1. **Market Orders**: Should we support market orders? (requires different params)
2. **Order History**: Should we add a tool to view order history (not just open orders)?
3. **Account Info**: Should we expose account/balance as tools or resources?
4. **Testing**: Use testnet or mainnet for testing? (testnet safer)
