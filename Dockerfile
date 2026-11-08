FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY data ./data
COPY src ./src

RUN uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "sentinelrag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
