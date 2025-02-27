# Use Bash for shell commands
SHELL := /bin/bash

# Project Name
PROJECT_NAME := "blogscraper"

.DEFAULT_GOAL := help

# Show this help message
.PHONY: help
help:
	@echo -e "\033[1;34mUsage:\033[0m make [target]"
	@echo ""
	@echo -e "\033[1;36mTargets:\033[0m"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	    helpMessage = match(lastComment, /^# (.*)/); \
	    helpCommand = $$1; sub(/:$$/, "", helpCommand); \
	    if (helpMessage) { \
	        printf "  \033[1;32m%-20s\033[0m \033[0;37m%s\033[0m\n", helpCommand, substr(lastComment, RSTART + 2, RLENGTH - 2); \
	    } else { \
	        printf "  \033[1;32m%-20s\033[0m \033[0;33m??? [No description]\033[0m\n", helpCommand; \
	    } \
	    lastComment = ""; \
	} \
	/^# / { \
	    lastComment = $$0; \
	} \
	/^\.PHONY:/ { \
	    next; \
	}' $(MAKEFILE_LIST) | sort
	@echo ""


# Setup the development environment
.PHONY: setup-dev-env
setup-dev-env: update install lint
	@echo "🚀 Setting up Git hooks..."
	poetry run pre-commit install
	@if [ -f .git/hooks/pre-commit ]; then chmod +x .git/hooks/pre-commit; fi
	@echo "✅ Development environment is ready!"


# Sync dependencies, updating poetry.lock and .venv
.PHONY: update
update:
	poetry update


# Install dependencies from poetry.lock
.PHONY: install
install:
	poetry install


# List all outdated dependencies (direct dependencies only)
.PHONY: outdated
outdated:
	poetry show --outdated --top-level


# List all outdated dependencies (including transitive dependencies)
.PHONY: outdated-all
outdated-all:
	poetry show --outdated


# Lint all files (fails on errors)
.PHONY: lint
lint:
	@echo "🔍 Running Ruff..."
	@poetry run ruff check . || lint_failed=1
	@echo "🔍 Running Pyright..."
	@poetry run pyright . || lint_failed=1
	@echo "🔍 Running Mypy..."
	@poetry run mypy . || lint_failed=1
	@exit $${lint_failed:-0}


# Run tests
.PHONY: test
test:
	poetry run pytest --maxfail=1 --disable-warnings


# Run test coverage (with 80% minimum threshold)
.PHONY: coverage
coverage:
	poetry run pytest --cov=. --cov-report=term-missing --cov-fail-under=80


# Generate an LLM-ready copy of this repo
.PHONY: as-llm-input
as-llm-input:
	poetry run gitingest -o dev-docs/blogscraper-digest.txt -e dev-docs


# Run the application
.PHONY: run
run:
	@echo "🚀 Running the application..."
	poetry run python -m blogscraper.main


# Debug the application with PDB
.PHONY: debug
debug:
	@echo "🐞 Running the application in debug mode..."
	poetry run python -m pdb -m blogscraper.main
