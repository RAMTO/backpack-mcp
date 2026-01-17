.PHONY: help setup venv install env clean test check-python

# Default target - runs full setup
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@echo "  make setup      - Run full setup (venv + install + env)"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make env        - Copy .env.example to .env (if missing)"
	@echo "  make clean      - Remove virtual environment"
	@echo "  make test       - Run integration tests"
	@echo "  make check-python - Check if Python 3 is available"

setup: check-python venv install env ## Run full setup (venv + install + env)
	@echo "✓ Setup complete!"
	@echo "  Next steps:"
	@echo "  1. Edit .env and add your Backpack API keys"
	@echo "  2. Run 'make test' to verify everything works"

venv: ## Create virtual environment
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
		echo "✓ Virtual environment created"; \
	else \
		echo "✓ Virtual environment already exists"; \
	fi

install: venv ## Install dependencies
	@echo "Installing dependencies..."
	@venv/bin/pip install --upgrade pip --quiet
	@venv/bin/pip install -r requirements.txt
	@echo "✓ Dependencies installed"

env: ## Copy .env.example to .env (if missing)
	@if [ ! -f ".env" ]; then \
		if [ -f ".env.example" ]; then \
			cp .env.example .env; \
			echo "✓ Created .env from .env.example"; \
			echo "  Please edit .env and add your API keys"; \
		else \
			echo "✗ Error: .env.example not found"; \
			exit 1; \
		fi; \
	else \
		echo "✓ .env already exists (not overwritten)"; \
	fi

clean: ## Remove virtual environment
	@if [ -d "venv" ]; then \
		echo "Removing virtual environment..."; \
		rm -rf venv; \
		echo "✓ Virtual environment removed"; \
	else \
		echo "✓ No virtual environment to remove"; \
	fi

test: venv ## Run integration tests
	@echo "Running integration tests..."
	@venv/bin/python test_integration.py

check-python: ## Check if Python 3 is available
	@if ! command -v python3 > /dev/null 2>&1; then \
		echo "✗ Error: python3 not found. Please install Python 3.8 or higher."; \
		exit 1; \
	fi
	@python3 --version
