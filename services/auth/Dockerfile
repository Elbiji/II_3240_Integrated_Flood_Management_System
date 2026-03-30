FROM python:3.12-slim

# Provided from uv's documentation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set workdir app
WORKDIR /app

# Cache layering strategy 
COPY pyproject.toml uv.lock ./

# Run uv to synchronize dependencies for now
RUN uv sync --frozen --no-install-project

# Copy whole project to container
COPY . .

# Run uv to install whole project
RUN uv sync --frozen

# Run service
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

