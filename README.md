# Backpack Exchange MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with tools to interact with the Backpack Exchange API. Manage your orders directly from Cursor or other MCP-compatible AI assistants.

## Features

- **List Orders**: View all open spot orders, optionally filtered by trading pair
- **Create Orders**: Place limit or market orders (buy/sell)
- **Cancel Orders**: Cancel specific orders by ID
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

### Direct Python Usage

You can also use the client directly in Python:

```python
from backpack_client import BackpackClient

client = BackpackClient()

# List orders
orders = client.get_orders()
print(f"Found {len(orders)} orders")

# Create order
order = client.create_order(
    symbol="BTC_USDC",
    side="Bid",
    orderType="Limit",
    quantity="0.001",
    price="80000",
    timeInForce="GTC"
)
print(f"Order created: {order['id']}")

# Cancel order
cancelled = client.cancel_order(order_id="12345", symbol="BTC_USDC")
print(f"Order cancelled: {cancelled['status']}")
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

Create a new order (limit or market).

**Parameters:**
- `symbol` (required): Trading pair (e.g., "BTC_USDC")
- `side` (required): "Bid" (buy) or "Ask" (sell)
- `orderType` (required): "Limit" or "Market"
- `quantity` (required): Order quantity
- `price` (optional): Limit price (required for Limit orders)
- `timeInForce` (optional): "GTC" (default), "IOC", or "FOK"

**Returns:**
- `success`: Boolean
- `order`: Order object with ID and details
- `error`: Error message (if failed)

**Example:**
```
Create a limit buy order for 0.001 BTC at $80,000
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

## Testing

Run the integration tests:

```bash
# Using virtual environment
venv/bin/python test_integration.py

# Or system Python
python3 test_integration.py
```

The tests verify:
- All tools work correctly
- Error handling
- Response structures
- Full workflow (create → list → cancel)

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

### Project Structure

- `auth.py`: Core authentication (ED25519 signing)
- `backpack_client.py`: API client wrapper with error handling
- `mcp_server.py`: MCP server exposing tools
- `examples/`: Example code for direct API usage

### Adding New Tools

1. Add method to `BackpackClient` in `backpack_client.py`
2. Add MCP tool in `mcp_server.py` using `@mcp.tool()` decorator
3. Test with integration tests

## License

This project is for personal use. Use at your own risk when trading.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the example code in `examples/`
- Verify your API keys and configuration
