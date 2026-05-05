FROM python:3.12-slim

WORKDIR /app

# Switch to Aliyun mirrors for faster apt downloads
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null; \
    :

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (with Aliyun mirror for pip/PyPI)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --no-install-project --frozen

# Copy project files
COPY . .

# Collect static files
RUN mkdir -p static_root && \
    uv run python manage.py collectstatic --noinput --clear

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
