# Настройка PostgreSQL в Replit для Django проектов

## Проблема

Django проекты часто используют кастомные переменные окружения для подключения к БД (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`), а Replit автоматически создает переменные с префиксом `PG*` (`PGHOST`, `PGUSER`, и т.д.).

**Без изменения settings.py** можно использовать Replit PostgreSQL, просто скопировав значения из `PG*` переменных в ваши `DB_*` переменные.

## Решение

### Шаг 1: Создание PostgreSQL базы данных

1. Откройте Tools → Database в Replit
2. Нажмите "Create database" → выберите PostgreSQL
3. Replit автоматически создаст следующие переменные окружения:
   - `PGHOST` - хост базы данных
   - `PGPORT` - порт (обычно 5432)
   - `PGUSER` - имя пользователя БД
   - `PGPASSWORD` - пароль
   - `PGDATABASE` - имя базы данных
   - `DATABASE_URL` - полная строка подключения

### Шаг 2: Получение значений для DB_* переменных

**Вариант A: Использовать helper-скрипт (рекомендуется)**

Создайте файл `setup_db_env.py`:

```python
#!/usr/bin/env python
import os

# Маппинг переменных
mapping = {
    'PGHOST': 'DB_HOST',
    'PGPORT': 'DB_PORT',
    'PGUSER': 'DB_USER',
    'PGPASSWORD': 'DB_PASSWORD',
    'PGDATABASE': 'DB_NAME',
}

print("Скопируйте эти значения в Replit Secrets:\n")
for pg_key, db_key in mapping.items():
    value = os.getenv(pg_key, 'НЕ НАЙДЕНО')
    print(f"{db_key} = {value}")
```

Запустите:
```bash
python setup_db_env.py
```

**Вариант B: Вручную через Replit Shell**

```bash
echo "DB_HOST=$PGHOST"
echo "DB_USER=$PGUSER"
echo "DB_PASSWORD=$PGPASSWORD"
echo "DB_NAME=$PGDATABASE"
echo "DB_PORT=$PGPORT"
```

### Шаг 3: Добавление переменных в Replit Secrets

1. Откройте панель Secrets (🔒 иконка слева в Replit)
2. Для каждой переменной:
   - Нажмите "+ New secret"
   - Введите имя (например, `DB_HOST`)
   - Вставьте значение из Шага 2
   - Нажмите "Add secret"

Необходимые переменные:
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

### Шаг 4: Проверка подключения

```bash
# Проверка конфигурации Django
python manage.py check --database default

# Применение миграций
python manage.py migrate

# Проверка таблиц
python manage.py dbshell
\dt
\q
```

### Шаг 5: Очистка (опционально)

Удалите helper-скрипт, если использовали:
```bash
rm setup_db_env.py
```

## Типичный settings.py для этой конфигурации

```python
import os
from dotenv import load_dotenv

load_dotenv(override=True, encoding="utf8")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
```

## Troubleshooting

### Ошибка: "connection refused"
- Убедитесь, что PostgreSQL база создана в Replit Database tool
- Проверьте, что все `DB_*` переменные установлены в Secrets

### Ошибка: "role does not exist"
- Проверьте, что `DB_USER` совпадает с `PGUSER`
- Пересоздайте переменные в Secrets

### Ошибка: "database does not exist"
- Проверьте, что `DB_NAME` совпадает с `PGDATABASE`
- Убедитесь, что база данных создана

### Миграции не применяются
```bash
# Проверьте статус миграций
python manage.py showmigrations

# Пересоздайте миграции если нужно
python manage.py makemigrations
python manage.py migrate
```

## Для продакшена (Windows localhost)

В `.env` файле на Windows используйте локальные значения:

```env
# Production (Windows localhost)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Преимущества этого подхода

✅ **Не требует изменения settings.py** - код остается универсальным  
✅ **Безопасность** - credentials хранятся в Replit Secrets, не в коде  
✅ **Совместимость** - один и тот же код работает в Replit и на Windows  
✅ **Простота** - автоматическое управление БД от Replit  

## Альтернатива: Использование DATABASE_URL

Если хотите использовать `DATABASE_URL` напрямую, можно использовать пакет `dj-database-url`:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
```

Но это требует изменения settings.py и установки дополнительного пакета.

## Заключение

Этот метод позволяет использовать Replit PostgreSQL в Django проектах без изменения существующего кода - просто скопируйте значения переменных из `PG*` в `DB_*` через Replit Secrets.
