# Use-C Bash for shell commands
SHELL := /bin/bash

# Project Name
PROJECT_NAME := blogscraper

.DEFAULT_GOAL := help

# Show help message
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

# Generate an LLM-ready copy of this repo. (Doesn't really work yet; just does backend)
.PHONY: as-llm-input
as-llm-input:
	poetry -C backend run gitingest https://github.com/deg/blogscraper \
	-o ../dev-docs/blogscraper-digest.txt \
	-e .specstory
	poetry -C backend run gitingest https://github.com/deg/degel-python-utils \
	-o ../dev-docs/degel-python-utils-digest.txt



# Setup the development environment
.PHONY: setup-dev-env
setup-dev-env: install lint
	@echo "🚀 Setting up Git hooks..."
	$(shell cd backend && poetry env info -p)/bin/pre-commit install
	@if [ -f .git/hooks/pre-commit ]; then chmod +x .git/hooks/pre-commit; fi
	@echo "✅ Development environment is ready!"



# Install dependencies
.PHONY: install
install:
	@echo "📦 Installing dependencies for backend..."
	@$(MAKE) -C backend install || exit 1
	@echo "📦 Installing dependencies for frontend..."
	@$(MAKE) -C frontend install || exit 1
	@echo "📦 Installation complete for all components."


# Run the docker container
.PHONY: docker-up
docker-up:
	docker compose up --build -d && docker compose logs -f blo_backend


# Clean the temp docker container
.PHONY: docker-down
docker-down:
	docker compose down --remove-orphans


# Run the backend
.PHONY: run-backend
run-backend:
	@$(MAKE) -C backend run


# Lint all components
.PHONY: lint
lint:
	@echo "🔍 Running lint in backend..."
	@$(MAKE) -C backend lint || exit 1
	@echo "🔍 Running lint in frontend..."
	@$(MAKE) -C frontend lint || exit 1
	@echo "✅ Linting completed for all components."


# Clean all components
.PHONY: clean
clean:
	@echo "🧹 Cleaning backend..."
	@$(MAKE) -C backend clean || exit 1
	@echo "🧹 Cleaning frontend..."
	@$(MAKE) -C frontend clean || exit 1
	@echo "🧹 Cleaned all components."


# List all outdated components
.PHONY: outdated
outdated:
	@echo "❗ Checking backend..."
	@$(MAKE) -C backend outdated || exit 1
	@echo "🧹 Checking frontend..."
	@$(MAKE) -C frontend outdated || exit 1
	@echo "🧹 Checked all components."

