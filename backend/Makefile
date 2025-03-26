# Install dependencies from poetry.lock
.PHONY: install
install:
	poetry update
	poetry install --extras dev
	poetry run playwright install


# Run the application
.PHONY: run
run:
	@echo "🚀 Running the application..."
	poetry run uvicorn blogscraper.main:app --host 0.0.0.0 --port 8000 --reload


# Lint all files (fails on errors)
.PHONY: lint
lint:
	@echo "🔍 Running Black..."
	@poetry run black --check . || lint_failed=1
	@echo "🔍 Running isort..."
	@poetry run isort --check-only src  || lint_failed=1
	@echo "🔍 Running Ruff..."
	@poetry run ruff check . || lint_failed=1
	@echo "🔍 Running Pyright..."
	@poetry run pyright . || lint_failed=1
	@echo "🔍 Running Mypy..."
	@poetry run mypy . || lint_failed=1
	@echo "🔍 Running Flake8..."
	@poetry run flake8 || lint_failed=1
	@exit $${lint_failed:-0}


# Clean all files
.PHONY: clean
clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .venv poetry.lock


# List all outdated dependencies (direct dependencies only)
.PHONY: outdated
outdated:
	poetry show --outdated --top-level


# List all unused code
.PHONY: unused
unused:
	poetry run vulture --ignore-decorators "@app.*" src/


# List all outdated dependencies (including transitive dependencies)
.PHONY: outdated-all
outdated-all:
	poetry show --outdated


##########
# These commands are not yet in the top-level Makefile
##########

# Run tests
.PHONY: test
test:
	poetry run pytest --maxfail=1 --disable-warnings


# Debug the application with PDB
.PHONY: debug
debug:
	@echo "🐞 Running the application in debug mode..."
	poetry run python -m pdb -m blogscraper.main


# Run test coverage (with 80% minimum threshold)
.PHONY: coverage
coverage:
	poetry run pytest --cov=. --cov-report=term-missing --cov-fail-under=80


