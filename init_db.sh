#!/bin/bash

# Выполняем миграции Alembic
echo "Запускаем миграции Alembic..."
echo "База данных готова, выполняем миграции..."
poetry run alembic upgrade head || { echo "Миграции не удались!"; exit 1; }

echo "База данных инициализирована!"
echo "Запуск приложения..."
exec "$@"