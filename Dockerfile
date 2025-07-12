FROM python:3.11-slim

WORKDIR /app

# Install curl and install uv to /root/.local/bin
RUN apt-get update && \
    apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy only dependency files first
COPY pyproject.toml ./

# Install dependencies
RUN uv synv

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 10003

# Run the app
CMD ["uv", "run", "."]
