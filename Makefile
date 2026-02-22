.PHONY: install run run-build-employee clean

# Install dependencies using uv and build the knowledge base
install:
	uv sync
	uv run scripts/create_kb_chroma.py

# Run the main application interactively
run:
	uv run main.py

run-build-employee:
	uv run scripts/build_employee.py

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
