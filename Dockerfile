FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY *.py ./
COPY data/sample_en.csv data/sample_tr.csv ./data/
COPY results/ ./results/

EXPOSE 8501
# TYPESAFE_API_KEY is passed at runtime (--env-file), never baked into the image.
CMD ["uv", "run", "--frozen", "--no-sync", "streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
