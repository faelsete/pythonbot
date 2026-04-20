FROM python:3.11-slim

# System dependencies for Playwright, ffmpeg and Node (for MCPs)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ffmpeg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install node for NPX server runners
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
COPY pythonbot /app/pythonbot
WORKDIR /app/pythonbot

# Sync dependencies using uv (no lockfile yet, so no --frozen)
RUN uv sync

# Install playwright browsers
RUN uv run playwright install chromium --with-deps

EXPOSE 8420

# Command to run daemon
CMD ["uv", "run", "pythonbot", "start"]
