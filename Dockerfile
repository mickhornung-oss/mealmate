FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
COPY alembic.ini ./
COPY start.sh ./
COPY .env.example ./.env.example

RUN chmod +x /app/start.sh && chown -R app:app /app

USER app

EXPOSE 8000
ENV PORT=8000

CMD ["./start.sh"]
