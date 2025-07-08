# Dockerfile

# --- Builder Stage ---
# Used to compile Python packages that need a build environment
FROM python:3.11-slim as builder

# Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt .

# Install dependencies. Using --prefix ensures they go to a predictable location.
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

# --- Production Stage ---
# The final, lean image
FROM python:3.11-slim

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd --system appuser && useradd --system --gid appuser appuser

# Copy installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY *.py ./

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set environment variables for the application
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
# Let Cloud Run set the --workers flag dynamically based on concurrency
CMD ["uvicorn", "src.useapi_mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]