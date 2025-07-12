FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl to get uv
RUN apt-get update && \
    apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for future layers
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy only pyproject.toml and other metadata first to leverage Docker cache
COPY pyproject.toml ./

# Install dependencies
RUN uv synv

# Now copy the rest of the application
COPY . .

# Expose port (as you said: 10003)
EXPOSE 10003

# Start the app
CMD ["uv", "run", "."]
