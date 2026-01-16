# Testing Guide

This guide explains how to run the tests for the Backpack MCP server.

## Available Tests

### Integration Test (`test_integration.py`)
Comprehensive integration test that verifies all MCP tools work together:
- Full workflow (Create → List → Cancel)
- Error handling
- Response structure validation

## Running Tests

### Option 1: Using Python Directly

```bash
cd /Users/martindobrev/Code/backpack-api

# Using system Python
python3 test_integration.py

# Using virtual environment (recommended)
venv/bin/python test_integration.py
```

### Option 2: Make it Executable

```bash
# Make the test script executable
chmod +x test_integration.py

# Run it directly
./test_integration.py
```

### Option 3: Using Python Module

```bash
cd /Users/martindobrev/Code/backpack-api
python3 -m pytest test_integration.py  # If pytest is installed
```

## Expected Output

When tests run successfully, you should see:

```
============================================================
Phase 8: Integration Testing & Polish
============================================================

Testing imports...
------------------------------------------------------------
✅ All MCP tools imported successfully
   MCP instance: FastMCP

============================================================
Scenario 1: Full Workflow (Create → List → Cancel)
============================================================
...

============================================================
Integration Test Summary
============================================================
Scenario 1 (Full Workflow): ✅ PASSED
Scenario 2 (Error Handling): ✅ PASSED
Scenario 3 (Response Structures): ✅ PASSED
============================================================

✅ All integration tests passed!
```

## Test Scenarios

### Scenario 1: Full Workflow
Tests the complete order lifecycle:
1. Creates a test order
2. Lists orders to verify it appears
3. Cancels the order

**Note**: This will create a real order on Backpack Exchange (at a price that won't execute immediately).

### Scenario 2: Error Handling
Tests error handling for:
- Invalid order IDs
- Missing required parameters
- Invalid input values
- Invalid symbols

### Scenario 3: Response Structure Validation
Verifies that all tools return properly structured responses with required fields.

## Prerequisites

Before running tests:

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure API keys** (in `.env` file):
   ```
   BACKPACK_PRIVATE_KEY=your_private_key
   BACKPACK_PUBLIC_KEY=your_public_key
   ```

3. **Ensure network access** (tests make real API calls)

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`:
```bash
# Make sure you're in the project directory
cd /Users/martindobrev/Code/backpack-api

# Use the virtual environment
venv/bin/python test_integration.py
```

### Network Errors
If you see network errors:
- Check your internet connection
- Verify API keys are correct
- Check if Backpack API is accessible

### API Errors
If tests fail with API errors:
- Verify you have sufficient funds for test orders
- Check that API keys have proper permissions
- Some errors are expected (e.g., invalid order IDs)

## Running Individual Tool Tests

You can also test individual tools directly:

```python
# Test list_orders
python3 -c "from mcp_server import list_orders; print(list_orders())"

# Test create_order (validation)
python3 -c "from mcp_server import create_order; print(create_order('BTC_USDC', 'Bid', 'Limit', '0.001'))"

# Test cancel_order (validation)
python3 -c "from mcp_server import cancel_order; print(cancel_order('', 'BTC_USDC'))"
```

## Continuous Testing

For development, you can run tests in watch mode (if you have `entr` or similar):

```bash
# Watch for file changes and re-run tests
find . -name "*.py" | entr -c python3 test_integration.py
```

## Test Coverage

The integration test covers:
- ✅ All three MCP tools
- ✅ Error handling
- ✅ Response structures
- ✅ Input validation
- ✅ Real API interactions (when network available)

## Next Steps

After running tests:
1. If all tests pass → Server is production-ready ✅
2. If tests fail → Check error messages and fix issues
3. Review logs for any warnings or errors
