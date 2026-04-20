FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl git ffmpeg \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN uv sync
RUN uv run playwright install chromium --with-deps || true

EXPOSE 8420

CMD ["uv", "run", "pythonbot", "start"]
