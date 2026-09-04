# Thin base image for paper-hub backend.
#
# Python dependencies are NOT installed here — uv sync runs
# on the host (cd backend && uv sync), and the resulting
# backend/.venv is bind-mounted into the container at /app/.venv.
#
# For production deployment, build a derivative image or CI
# step that runs uv sync before bundling.

FROM python:3.14-slim

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

# Install uv runtime (needed for uv run in CMD / compose command)
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# Copy project source (overridden in dev by ./backend:/app bind mount)
COPY backend/ .

EXPOSE 8000

# Default command (only works when .venv is present at /app/.venv,
# e.g. via bind mount from host's backend/.venv).
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
