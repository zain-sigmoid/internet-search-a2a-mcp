FROM python:3.11-slim

WORKDIR /app

# Install curl and uv
RUN apt-get update && \
    apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"
ENV PORT=10003

# Copy pyproject + lockfile
COPY pyproject.toml ./

# Install dependencies
RUN uv sync

# Copy entire project
COPY . .

# Expose app port
EXPOSE ${PORT}

# Use uv to run the Python file directly
CMD ["uv", "run", "server_railway.py"]
