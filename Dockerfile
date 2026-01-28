FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

RUN pip install --no-cache-dir discord.py mcp PyYAML

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "discord_mcp"]
