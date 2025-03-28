# Use an official lightweight Python image
FROM python:3.11-slim AS base

# Set the working directory inside the container
WORKDIR /app

# Install Playwright system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN apt-get update && apt-get install -y \
    libnss3 libatk-bridge2.0-0 libxss1 libasound2 libxcomposite1 libxrandr2 libgtk-3-0 libgbm1 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*


# Install Poetry (matching version from local system)
RUN pip install --no-cache-dir poetry==2.1.1

# Copy only the dependency files first to optimize caching
#- COPY pyproject.toml poetry.lock README.md ./
COPY pyproject.toml README.md ./

# Configure Poetry to create the virtual environment inside the project directory
RUN poetry config virtualenvs.in-project true

# Ensure Poetry detects the project correctly
RUN poetry install --no-interaction --no-ansi --no-root

# Finish Playwright setup
RUN poetry run playwright install chromium

# Copy the remaining project files
COPY . .

# Set Python path to allow execution from /app
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/app/src

# Set an unprivileged user for security
RUN useradd -m appuser
USER appuser

# Default command to run the scraper
# CMD ["poetry", "run", "uvicorn", "blogscraper.main:app", "--host", "0.0.0.0", "--port", "8000"]
