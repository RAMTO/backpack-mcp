# 🎒 Backpack Exchange MCP Server

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
backpack-mcp/
├── auth.py                 # ED25519 authentication module
├── backpack_client.py      # Backpack API client wrapper
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
cd backpack-mcp
```

### 2. Install Dependencies

```bash
# Using pip
pip3 install -r requirements.txt

# Or using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
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

**To generate key pair:**
```
python3 -c "from cryptography.hazmat.primitives.asymmetric import ed25519; import base64; key = ed25519.Ed25519PrivateKey.generate(); seed = key.private_bytes_raw(); pub = key.public_key().public_bytes_raw(); print(f'Seed: {base64.b64encode(seed).decode()}\nPublic Key: {base64.b64encode(pub).decode()}')"
```

**To get your API key:**
1. Log in to [Backpack Exchange](https://backpack.exchange)
2. Go to Settings > API Keys
3. Click New API key
4. Add the public key
5. Add the generated key pair to your `.env` file

## Usage

### MCP Server (Recommended)

The MCP server allows AI assistants like Cursor to interact with your Backpack account.

#### Setup in Cursor

1. **Create MCP configuration** at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "backpack": {
      "command": "/path/to/backpack-mcp/venv/bin/python",
      "args": [
        "/path/to/backpack-mcp/mcp_server.py"
      ]
    }
  }
}
```

**Important**: Replace `/path/to/backpack-mcp` with the actual path to your project directory. For example:
- On macOS/Linux: `/Users/yourusername/Code/backpack-mcp` or `~/Code/backpack-mcp`
- On Windows: `C:\Users\yourusername\Code\backpack-mcp`

You can find your project path by running `pwd` (macOS/Linux) or `cd` (Windows) in your project directory.

**Why API keys aren't in the MCP configuration:**

The MCP configuration (`~/.cursor/mcp.json`) only tells Cursor where to find the Python script and interpreter. It does **not** contain your API keys. This is a security best practice:

- **Separation of concerns**: Configuration (where to run code) is separate from credentials (API keys)
- **Security**: The `.env` file with your keys is gitignored and never committed
- **Runtime loading**: The MCP server loads keys from `.env` when it starts, not from the MCP config
- **Flexibility**: You can change keys without modifying the MCP configuration

**How ED25519 key pairs connect to subaccounts:**

According to the [official Backpack Exchange API documentation](https://docs.backpack.exchange):

1. **One key pair per main account**: The ED25519 key pair (public/private) authenticates your **main Backpack account**, not individual subaccounts.

2. **Subaccounts are identified by parameter**: When you want to use a specific subaccount, you include `subaccountId` as a parameter in API requests. The same key pair authenticates all subaccounts under your main account.

3. **No separate keys needed**: You do **not** need different key pairs for different subaccounts. One key pair gives you access to all subaccounts, and you specify which one to use via the `subaccountId` parameter.

**Example flow:**
- Generate one ED25519 key pair in Backpack Exchange settings
- Store it in `.env` (BACKPACK_PRIVATE_KEY and BACKPACK_PUBLIC_KEY)
- The MCP server uses these keys to sign all requests
- To access a specific subaccount, include `subaccountId` in the request parameters (if the endpoint supports it)

2. **Restart Cursor** completely (quit and reopen)

3. **Use the tools** by asking Cursor:
   - "List my open orders"
   - "Create a limit buy order for 0.001 BTC at $80,000"
   - "Cancel order 12345 for BTC_USDC"
   - "Show my positions"
   - "Get my balances"
   - "Open a long position in SOL_USDC_PERP for $10"

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

## License

This project is for personal use. Use at your own risk when trading.
