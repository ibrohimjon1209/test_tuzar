FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
        tesseract-ocr \
        poppler-utils \
        curl \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 10001 appgroup \
    && useradd -r -u 10001 -g appgroup -d /app -s /usr/sbin/nologin appuser \
    && mkdir -p /app /data \
    && chown -R appuser:appgroup /app /data

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app /data

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import subprocess, sys; p = subprocess.run(['ps', '-eo', 'comm='], capture_output=True, text=True, check=False); sys.exit(0 if 'python' in p.stdout else 1)"

CMD ["python", "main.py"]
