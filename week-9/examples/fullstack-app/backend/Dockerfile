FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
RUN uv sync --no-dev

COPY main.py .

CMD ["uv", "run", "python", "main.py"]

# Made with Bob
