# TeamFinder

TeamFinder — платформа для поиска команды и совместной работы над pet-проектами. Пользователи могут публиковать идеи, находить участников, добавлять проекты в избранное и поддерживать профиль с контактами.

## Технологии

- Python 3.12+
- Django 5.2
- PostgreSQL
- Pillow (генерация аватаров)
- python-decouple (настройки через .env)

## Локальный запуск

### 1. Виртуальное окружение

```bash
python -m venv venv
```

Активация:

- Windows (PowerShell):
  ```bash
  venv\Scripts\Activate.ps1
  ```
- Windows (cmd):
  ```bash
  venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

### 2. Файл .env

Скопируйте пример и укажите параметры окружения:

```bash
cp .env_example .env
```

Пример заполнения .env:

```bash
DJANGO_SECRET_KEY=change_me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

TASK_VERSION=1
```

### 3. PostgreSQL через Docker

```bash
docker compose up -d
```

Остановить контейнеры:

```bash
docker compose down
```

### 4. Миграции

```bash
python manage.py migrate
```

### 5. Тестовые данные (опционально)

Команда создаёт нескольких пользователей и проекты:

```bash
python manage.py seed_demo
```

Данные для входа (пароль одинаковый):

- alina@example.com / demo12345
- andrey@example.com / demo12345
- alena@example.com / demo12345

Создание пользователя с доступом в Админ-панель:

```bash
python manage.py createsuperuser
```

### 6. Запуск сервера

```bash
python manage.py runserver
```

Проект доступен по адресу: http://localhost:8000

## Запуск тестов

```bash
python manage.py test
```
