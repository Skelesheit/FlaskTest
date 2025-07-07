#!/bin/bash

# Убедимся, что база данных готова
until pg_isready -h db -U user -d flask_db; do
  echo "Ожидаем готовности базы данных..."
  sleep 2
done

# Выполняем миграции Alembic
echo "Запускаем миграции Alembic..."
poetry run alembic upgrade head

echo "База данных инициализирована!"