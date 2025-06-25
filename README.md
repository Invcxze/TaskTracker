# TaskTracker - Веб-платформа для трекинга задач
## Запуск проекта локально

### Зависимости

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — современный инструмент для управления зависимостями Python

---

## Backend (Django)

### Установка

```bash
uv sync                        # Установка зависимостей из pyproject.toml
uv run manage.py migrate       # Применение миграций
uv run manage.py runserver     # Запуск сервера разработки
```

### Дополнительные команды

- Добавить новую библиотеку:

```bash
uv add <название_библиотеки>
```

- Быстрая установка библиотеки (без фиксации в pyproject.toml):

```bash
uv pip install <название_библиотеки>
```

- Создание миграций:

```bash
uv run manage.py makemigrations
```
- Запуск проекта через docker:
```bash
docker compose up --build -d
```
---
