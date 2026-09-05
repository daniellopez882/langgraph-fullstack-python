# This is a LangGraph deployment: the graph, the auth hook and the FastHTML UI
# are wired together by langgraph.json and run by the LangGraph server. The
# image installs the project and runs `langgraph dev` (in-memory server).
#
# For a production deployment, `langgraph build` produces an optimised image
# from the same langgraph.json; this Dockerfile is the simple, self-contained
# path for running the whole thing in one container.
FROM python:3.12-slim

RUN useradd --create-home --uid 10001 agent

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    LANGGRAPH_URL=http://127.0.0.1:2024

COPY pyproject.toml langgraph.json ./
COPY src/ ./src/
RUN pip install --upgrade pip && pip install . "langgraph-cli[inmem]>=0.1.83"

RUN chown -R agent:agent /app
USER agent
EXPOSE 2024

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:2024/ok', timeout=4).status == 200 else 1)"]

CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024", "--no-browser"]
