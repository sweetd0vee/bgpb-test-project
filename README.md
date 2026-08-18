# BGPB test project

Решение тестового задания: SQL-запросы по витрине кредитов и ML-пайплайн
предсказания дефолта.

## Структура

- [`1. SQL task/`](1.%20SQL%20task/README.md) — PostgreSQL-запросы, схема и тестовые данные.
  Сдаваемый файл: [`1. SQL task/queries/SQL-task.sql`](1.%20SQL%20task/queries/SQL-task.sql).
- [`2. ML task/`](2.%20ML%20task/README.md) — обучение XGBoost, оценка качества, FastAPI и Docker.

## Быстрый старт

### SQL

Нужен PostgreSQL 12+. Из каталога `1. SQL task`:

```bash
psql -d <database> -f schemas/create_tables.sql
psql -d <database> -f schemas/data.sql
psql -d <database> -f queries/task-1.sql
```

Полный скрипт со схемой, данными и всеми семью запросами: `queries/SQL-task.sql`.

### ML

Python 3.10+. Из каталога `2. ML task`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train.py
python evaluate.py
uvicorn app:app --reload
```

Подробности, формат CSV, метрики и Docker — в README каждой части.
