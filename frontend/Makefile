# Install dependencies
.PHONY: install
install:
	@echo "🚧 No install yet for frontend"


# Generate API client from OpenAPI spec
.PHONY: gen-api
gen-api:
	curl -s http://localhost:8000/openapi.json | jq . > openapi/schema.json
	yarn orval --config openapi/orval.config.ts


# Lint all files (fails on errors)
.PHONY: lint
lint:
	@echo "🚧 No lint yet for frontend"


# Clean work product files
.PHONY: clean
clean:
	@echo "🚧 No clean yet for frontend"


# List all outdated dependencies (direct dependencies only)
.PHONY: outdated
outdated:
	@echo "🚧 No outdated yet for frontend"


# List all unused code
.PHONY: unused
unused:
	@echo "🚧 No outdated yet for frontend"
