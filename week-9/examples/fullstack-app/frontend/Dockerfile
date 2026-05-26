FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
RUN uv sync --no-dev

COPY app.py .

CMD [
  "uv",
  "run",
  "streamlit",
  "run",
  "app.py",
  "--server.port=8501",
  "--server.address=0.0.0.0",
  "--server.headless=true"
]

