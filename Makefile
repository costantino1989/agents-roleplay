.PHONY: install run run-luigi run-francesca clean

# Install dependencies using uv and build the knowledge base
install:
	uv sync
	uv run scripts/create_kb_chroma.py

# Run the main application interactively
run:
	uv run main.py

# Run the application with Luigi profile
run-luigi:
	uv run main.py --profile Luigi

# Run the application with Francesca profile
run-francesca:
	uv run main.py --profile Francesca

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
