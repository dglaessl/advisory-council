# Council CrewAI strategy panels. Build with run.sh (it supplies the bridge context):
#   docker build --build-context bridge=<repo>/bridge -t council-crewai:1.15.33 external/crewai
# Needs BuildKit (default in Docker Desktop / Docker Engine 23+) for --build-context.
ARG BASE_IMAGE=python:3.13-slim
FROM ${BASE_IMAGE}

ARG WITH_SEARCH=0
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OTEL_SDK_DISABLED=true \
    CREWAI_DISABLE_TELEMETRY=true \
    CREWAI_DISABLE_TRACKING=true \
    CREWAI_TRACING_ENABLED=false \
    BRIDGE_PY=/app/bridge/bridge.py \
    HOME=/tmp

WORKDIR /app
COPY requirements.txt requirements-search.txt constraints.txt ./
RUN python -m pip install -r requirements.txt -c constraints.txt \
 && if [ "$WITH_SEARCH" = "1" ]; then python -m pip install -r requirements-search.txt; fi

# bridge.py is the authority on envelope rules; copied in at build time so the
# container needs no repo mount.
COPY --from=bridge bridge.py /app/bridge/bridge.py
COPY crews/ /app/crews/

# Unprivileged by default; run.sh also passes --user to match the host owner of /out.
USER 10001:10001

ENTRYPOINT ["python", "-I", "/app/crews/dispatch.py"]
