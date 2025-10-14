# Этап 1: Установка зависимостей
FROM python:3.12-slim as requirements-stage

RUN python3 -m pip install poetry==2.1.3 poetry-plugin-export
COPY pyproject.toml poetry.lock ./
RUN python3 -m poetry export -f requirements.txt --output requirements.txt

# Этап 2: Финальный образ
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем сгенерированные требования
COPY --from=requirements-stage requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /server

WORKDIR /server

ENTRYPOINT ["gunicorn", "main:create_application()", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]