# Backpack Exchange MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with tools to interact with the Backpack Exchange API. Manage your orders directly from Cursor or other MCP-compatible AI assistants.

## Features

- **Order Management**:
  - List open spot orders (optionally filtered by trading pair)
  - Create limit or market orders (buy/sell) for both SPOT and PERP markets
  - Cancel specific orders by ID
- **Position Management**:
  - List all open perpetual positions with PnL, entry price, liquidation price, etc.
- **Account Management**:
  - Get account balances (available, locked, staked, and lent funds)
- **Secure Authentication**: ED25519 signature-based authentication
- **Local-Only**: Uses stdio transport for secure local communication

## Project Structure

```
backpack-api/
├── auth.py                 # ED25519 authentication module
├── backpack_client.py       # Backpack API client wrapper
├── mcp_server.py           # MCP server with tools
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your API keys (not in git)
├── examples/               # Example code
│   └── example_auth.py     # Direct API usage examples
└── test_integration.py     # Integration tests
```

## Installation

### 1. Clone or Navigate to Project

```bash
cd backpack-api
```

### 2. Install Dependencies

```bash
# Using pip
pip3 install -r requirements.txt

# Or using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example environment file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` and add your Backpack Exchange API keys:

```env
BACKPACK_PRIVATE_KEY=your_base64_encoded_private_key
BACKPACK_PUBLIC_KEY=your_base64_encoded_public_key
```

**To get your API keys:**
1. Log in to [Backpack Exchange](https://backpack.exchange)
2. Go to Settings > API Keys
3. Generate a new ED25519 key pair
4. Base64 encode both keys
5. Add them to your `.env` file

## Usage

### MCP Server (Recommended)

The MCP server allows AI assistants like Cursor to interact with your Backpack account.

#### Setup in Cursor

1. **Create MCP configuration** at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "backpack": {
      "command": "/Users/martindobrev/Code/backpack-api/venv/bin/python",
      "args": [
        "/Users/martindobrev/Code/backpack-api/mcp_server.py"
      ]
    }
  }
}
```

**Note**: Update the paths to match your system.

2. **Restart Cursor** completely (quit and reopen)

3. **Use the tools** by asking Cursor:
   - "List my open orders"
   - "Create a limit buy order for 0.001 BTC at $80,000"
   - "Cancel order 12345 for BTC_USDC"
   - "Show my positions"
   - "Get my balances"
   - "Open a long position in SOL_USDC_PERP for $10"

### Direct Python Usage

You can also use the client directly in Python:

```python
from backpack_client import BackpackClient

client = BackpackClient()

# List orders
orders = client.get_orders()
print(f"Found {len(orders)} orders")

# Create order (SPOT or PERP)
order = client.create_order(
    symbol="BTC_USDC",  # or "BTC_USDC_PERP" for perpetual
    side="Bid",
    orderType="Limit",
    quantity="0.001",
    price="80000",
    timeInForce="GTC"
)
print(f"Order created: {order['id']}")

# Create market order with quote quantity (for PERP)
perp_order = client.create_order(
    symbol="SOL_USDC_PERP",
    side="Bid",
    orderType="Market",
    quoteQuantity="10"  # $10 worth
)
print(f"Perp order created: {perp_order['id']}")

# Cancel order
cancelled = client.cancel_order(order_id="12345", symbol="BTC_USDC")
print(f"Order cancelled: {cancelled['status']}")

# List positions
positions = client.get_positions()
print(f"Found {len(positions)} positions")
for pos in positions:
    print(f"{pos['symbol']}: {pos['netQuantity']} (PnL: {pos['pnlUnrealized']})")

# Get balances (including lent funds)
balances = client.get_balances()
for asset, bal in balances.items():
    total = float(bal['available']) + float(bal['locked']) + float(bal['staked']) + float(bal['lent'])
    if total > 0:
        print(f"{asset}: Available={bal['available']}, Lent={bal['lent']}")
```

## Available MCP Tools

### `list_orders`

List all open spot orders.

**Parameters:**
- `symbol` (optional): Trading pair filter (e.g., "BTC_USDC")

**Returns:**
- `orders`: List of order objects
- `count`: Number of orders
- `symbol`: Filter used

**Example:**
```
List my open orders
List my BTC_USDC orders
```

### `create_order`

Create a new order (limit or market). Works for both SPOT and PERP markets.

**Parameters:**
- `symbol` (required): Trading pair (e.g., "BTC_USDC" for spot, "BTC_USDC_PERP" for perpetual)
- `side` (required): "Bid" (buy) or "Ask" (sell)
- `orderType` (required): "Limit" or "Market"
- `quantity` (optional): Order quantity (required for limit orders, optional for market if quoteQuantity provided)
- `price` (optional): Limit price (required for Limit orders)
- `timeInForce` (optional): "GTC" (default), "IOC", or "FOK"
- `quoteQuantity` (optional): Quote quantity for market orders (e.g., "10" for $10 worth)

**Returns:**
- `success`: Boolean
- `order`: Order object with ID and details
- `error`: Error message (if failed)

**Example:**
```
Create a limit buy order for 0.001 BTC at $80,000
Open a long position in SOL_USDC_PERP for $10 (market order)
```

### `cancel_order`

Cancel a specific order by ID.

**Parameters:**
- `orderId` (required): Order ID to cancel
- `symbol` (required): Trading pair (e.g., "BTC_USDC")

**Returns:**
- `success`: Boolean
- `order`: Cancelled order object
- `error`: Error message (if failed)

**Example:**
```
Cancel order 12345 for BTC_USDC
```

### `list_positions`

List all open perpetual positions.

**Parameters:**
- None

**Returns:**
- `positions`: List of position objects with:
  - `symbol`: Trading pair
  - `netQuantity`: Net quantity (positive = long, negative = short)
  - `entryPrice`: Entry price
  - `markPrice`: Current mark price
  - `pnlUnrealized`: Unrealized profit/loss
  - `pnlRealized`: Realized profit/loss
  - `estLiquidationPrice`: Estimated liquidation price
  - And more...
- `count`: Number of positions

**Example:**
```
Show my positions
List my perpetual positions
```

### `get_balances`

Get all account balances including lent funds.

**Parameters:**
- `showZeroBalances` (optional): If False (default), only show assets with non-zero balances. If True, show all assets.

**Returns:**
- `balances`: Dictionary with asset symbols as keys, each containing:
  - `available`: Available balance (can be used for trading)
  - `locked`: Locked balance (committed to open orders)
  - `staked`: Staked balance (staked for rewards)
  - `lent`: Lent balance (funds currently lent out, earning interest)
- `count`: Number of assets with non-zero balances
- `totalAssets`: Total number of assets

**Example:**
```
Get my balances
Show my account balances
```

## Testing

Run the integration tests:

```bash
# Using virtual environment
venv/bin/python test_integration.py

# Or system Python
python3 test_integration.py
```

The tests verify:
- **Scenario 1**: Full workflow (create → list → cancel orders)
- **Scenario 2**: Error handling for all tools
- **Scenario 3**: Response structure validation
- **Scenario 4**: Positions functionality
- **Scenario 5**: Balances functionality (including lent funds)

All tests are integrated into `test_integration.py` and cover:
- Order management (list, create, cancel)
- Position management (list positions)
- Account management (get balances with lent funds)
- Error handling and edge cases

## Security

- **Local-Only**: MCP server uses stdio transport (no network exposure)
- **Environment Variables**: API keys stored in `.env` (gitignored)
- **ED25519 Signing**: All requests are cryptographically signed
- **No Key Logging**: Logging redacts sensitive information

## Requirements

- Python 3.8+
- Backpack Exchange API keys (ED25519)
- Dependencies (see `requirements.txt`):
  - `mcp[cli]` - MCP Python SDK
  - `requests` - HTTP client
  - `cryptography` - ED25519 signing
  - `python-dotenv` - Environment variables

## Troubleshooting

### MCP Server Not Connecting

1. **Check Python path** in `~/.cursor/mcp.json` matches your system
2. **Restart Cursor** completely after configuration changes
3. **Verify dependencies**: `pip3 install -r requirements.txt`
4. **Check API keys**: Ensure `.env` file exists with valid keys

### Import Errors

```bash
# Make sure you're using the virtual environment
venv/bin/python -c "from mcp_server import list_orders; print('OK')"
```

### API Errors

- Verify API keys are correct and base64-encoded
- Check you have sufficient funds for orders
- Ensure network connectivity to `api.backpack.exchange`

## Development

### Implementation Phases

The project follows a phased implementation approach (see `docs/MCP_PHASED_PLAN.md`):

**Completed Phases:**
- ✅ **Phase 0-8**: Setup, MCP server, order management (list, create, cancel)
- ✅ **Phase 9-10**: Position management (list perpetual positions)
- ✅ **Phase 11-12**: Account management (get balances including lent funds)

**Current Status:**
- Production-ready MCP server with order, position, and balance tools
- All core trading functionality implemented
- Comprehensive integration tests

### Project Structure

- `auth.py`: Core authentication (ED25519 signing)
- `backpack_client.py`: API client wrapper with error handling
- `mcp_server.py`: MCP server exposing tools
- `examples/`: Example code for direct API usage
- `docs/`: Documentation including phased implementation plan
- `test_integration.py`: Comprehensive integration tests

### Adding New Tools

1. Add method to `BackpackClient` in `backpack_client.py`
2. Add MCP tool in `mcp_server.py` using `@mcp.tool()` decorator
3. Add tests to `test_integration.py` as a new scenario
4. Update `docs/MCP_PHASED_PLAN.md` with new phases
5. Update this README with new tool documentation

## License

This project is for personal use. Use at your own risk when trading.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the example code in `examples/`
- Verify your API keys and configuration
