# Руководство по Management-командам проекта

## Обзор

Этот документ описывает все кастомные management-команды Django, используемые в проекте для управления email-рассылками.

---

## Кастомные команды

### 1. `send_mailing` — Отправка email-рассылки

**Назначение:** Ручная отправка email-рассылки по указанному ID через командную строку.

**Расположение:** `apps/mailings/management/commands/send_mailing.py`

#### Синтаксис

```bash
poetry run python manage.py send_mailing <mailing_id> [options]
```

#### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `mailing_id` | integer | ✅ Да | ID рассылки для отправки |
| `-v`, `--verbosity` | 0/1/2/3 | ❌ Нет | Уровень детализации вывода (по умолчанию: 1) |

#### Что делает команда

1. Проверяет существование рассылки с указанным ID
2. Проверяет статус рассылки (должен быть "Created")
3. Изменяет статус на "Running"
4. Отправляет email всем получателям из списка
5. Создаёт запись `Attempt` для каждой попытки отправки с:
   - `run_number` — номер текущего запуска
   - `trigger_type` — "command" (запуск через команду)
   - `status` — "success" или "failure"
   - `server_response` — результат отправки или текст ошибки
6. **Изменяет статус на "Completed" ВСЕГДА** (даже если были ошибки)

**Важно:** Команда завершает рассылку независимо от результата отправки отдельным получателям. Если часть писем не отправлена, рассылка всё равно получит статус "Completed", но записи `Attempt` будут содержать информацию об ошибках. Для повторной отправки только неудачным получателям нужно вручную изменить статус рассылки на "Created" через UI.

#### Примеры использования

**Windows (cmd):**
```cmd
:: Отправить рассылку с ID=1
poetry run python manage.py send_mailing 1

:: С подробным выводом
poetry run python manage.py send_mailing 1 -v 2

:: С максимальной детализацией
poetry run python manage.py send_mailing 1 --verbosity=3
```

**Windows (PowerShell):**
```powershell
# Отправить рассылку с ID=1
poetry run python manage.py send_mailing 1

# С подробным выводом
poetry run python manage.py send_mailing 1 -v 2
```

**Linux/macOS:**
```bash
# Отправить рассылку с ID=1
poetry run python manage.py send_mailing 1

# С подробным выводом
poetry run python manage.py send_mailing 1 -v 2
```

#### Возможные ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Рассылка с ID X не найдена` | Указан несуществующий ID | Проверьте ID рассылки в админке/UI |
| `Рассылка уже отправлена` | Статус не "Created" | Измените статус рассылки на "Created" через UI |
| `SMTPException` | Ошибка SMTP-сервера | Проверьте настройки EMAIL в `.env` |

#### Пример вывода

**При verbosity=1 (по умолчанию):**
```
Начинаю отправку рассылки #1 для 5 получателей...

Рассылка #1 завершена. Успешно: 5, Ошибки: 0
```

**При verbosity=2:**
```
Начинаю отправку рассылки #1 для 5 получателей...
  ✓ Отправлено: user1@example.com
  ✓ Отправлено: user2@example.com
  ✓ Отправлено: user3@example.com
  ✓ Отправлено: user4@example.com
  ✓ Отправлено: user5@example.com

Рассылка #1 завершена. Успешно: 5, Ошибки: 0
```

**При наличии ошибок (verbosity=1):**
```
Начинаю отправку рассылки #1 для 5 получателей...
  ✗ Ошибка для user3@example.com: [Errno 111] Connection refused

Рассылка #1 завершена. Успешно: 4, Ошибки: 1
```

**Примечание:** Даже при наличии ошибок рассылка получает статус "Completed". Проверьте таблицу `Attempt` для анализа неудачных отправок.

---

### 2. `create_managers_group` — Создание группы менеджеров

**Назначение:** Создание Django-группы "Managers" с необходимыми permissions для доступа менеджеров к функциям администрирования.

**Расположение:** `apps/users/management/commands/create_managers_group.py`

#### Синтаксис

```bash
poetry run python manage.py create_managers_group [options]
```

#### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `-v`, `--verbosity` | 0/1/2/3 | ❌ Нет | Уровень детализации вывода (по умолчанию: 1) |

#### Что делает команда

1. ✅ Создаёт группу "Managers" (или обновляет существующую)
2. ✅ Назначает следующие permissions:
   - `view_user` — просмотр пользователей
   - `view_recipient` — просмотр получателей
   - `view_message` — просмотр сообщений
   - `view_mailing` — просмотр рассылок
   - `can_view_all_recipients` — просмотр всех получателей (любых владельцев)
   - `can_view_all_messages` — просмотр всех сообщений (любых владельцев)
   - `can_view_all_mailings` — просмотр всех рассылок (любых владельцев)
   - `change_user` — изменение пользователей (для блокировки через `is_active`)
   - `can_disable_mailing` — отключение рассылок (через `is_active`)

#### Когда использовать

- 🔹 При первичной настройке проекта (после миграций)
- 🔹 При обновлении permissions для существующей группы
- 🔹 При восстановлении случайно удалённой группы

#### Примеры использования

**Windows (cmd/PowerShell):**
```cmd
:: Создать группу Managers
poetry run python manage.py create_managers_group

:: С подробным выводом всех permissions
poetry run python manage.py create_managers_group -v 2
```

**Linux/macOS:**
```bash
# Создать группу Managers
poetry run python manage.py create_managers_group

# С подробным выводом всех permissions
poetry run python manage.py create_managers_group -v 2
```

#### Пример вывода

**При verbosity=1 (по умолчанию):**
```
Группа "Managers" успешно создана.
Группа "Managers" настроена. Назначено 9 permissions.
```

**При verbosity=2:**
```
Группа "Managers" успешно создана.

Добавлены следующие permissions:
  - view_user (Can view Пользователь)
  - view_recipient (Can view Получатель)
  - view_message (Can view Сообщение)
  - view_mailing (Can view Рассылка)
  - can_view_all_recipients (Может просматривать всех получателей)
  - can_view_all_messages (Может просматривать все сообщения)
  - can_view_all_mailings (Может просматривать все рассылки)
  - change_user (Can change Пользователь)
  - can_disable_mailing (Может отключать рассылки)

Группа "Managers" настроена. Назначено 9 permissions.
```

#### После выполнения команды

1. Назначьте пользователя в группу "Managers" через Django Admin:
   ```
   http://localhost:5000/admin/auth/user/<user_id>/change/
   ```

2. Или через Python shell:
   ```python
   from django.contrib.auth import get_user_model
   from django.contrib.auth.models import Group
   
   User = get_user_model()
   user = User.objects.get(email='manager@example.com')
   managers_group = Group.objects.get(name='Managers')
   user.groups.add(managers_group)
   ```

---

## Стандартные Django-команды

### Миграции

```bash
# Применить все миграции
poetry run python manage.py migrate

# Создать новую миграцию (после изменения моделей)
poetry run python manage.py makemigrations

# Показать список миграций
poetry run python manage.py showmigrations

# Показать SQL для миграции
poetry run python manage.py sqlmigrate mailings 0008
```

### Работа с пользователями

```bash
# Создать суперпользователя
poetry run python manage.py createsuperuser

# Изменить пароль пользователя
poetry run python manage.py changepassword user@example.com
```

### Запуск сервера

```bash
# Запустить development-сервер
poetry run python manage.py runserver

# Запустить на 0.0.0.0:5000
poetry run python manage.py runserver 0.0.0.0:5000

# Запустить на другом порту
poetry run python manage.py runserver 8000
```

### Работа со статикой

```bash
# Собрать статические файлы (для production)
poetry run python manage.py collectstatic

# Удалить старые статические файлы и собрать заново
poetry run python manage.py collectstatic --clear --noinput
```

### Shell

```bash
# Django shell (стандартный)
poetry run python manage.py shell

# Django shell с IPython (если установлен)
poetry run python manage.py shell

# Выполнить Python-код напрямую
poetry run python manage.py shell -c "from apps.users.models import User; print(User.objects.count())"
```

### Проверка проекта

```bash
# Проверить конфигурацию Django
poetry run python manage.py check

# Проверить готовность к production
poetry run python manage.py check --deploy

# Проверить базу данных
poetry run python manage.py migrate --check
```

### Очистка кэша

```bash
# Очистить весь кэш
poetry run python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache cleared')"
```

---

## Типичные сценарии использования

### Сценарий 1: Первичная настройка проекта

```bash
# 1. Установить зависимости
poetry install

# 2. Применить миграции
poetry run python manage.py migrate

# 3. Создать группу Managers
poetry run python manage.py create_managers_group

# 4. Создать суперпользователя
poetry run python manage.py createsuperuser

# 5. Запустить сервер
poetry run python manage.py runserver 0.0.0.0:5000
```

### Сценарий 2: Ручная отправка рассылки

```bash
# 1. Проверить ID рассылки в UI: http://localhost:5000/mailings/

# 2. Отправить рассылку
poetry run python manage.py send_mailing 5 -v 2

# 3. Проверить результат в UI: http://localhost:5000/attempts/
```

### Сценарий 3: Повторная отправка рассылки

```bash
# 1. Изменить статус рассылки на "Created" через UI
#    http://localhost:5000/mailings/<id>/update/

# 2. Отправить рассылку снова (создастся новый run_number)
poetry run python manage.py send_mailing 5 -v 2

# 3. В истории будет два запуска: #1 и #2
```

### Сценарий 4: Назначение менеджера

```bash
# 1. Убедиться, что группа Managers создана
poetry run python manage.py create_managers_group

# 2. Назначить пользователя в группу через shell
poetry run python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from django.contrib.auth.models import Group
>>> User = get_user_model()
>>> user = User.objects.get(email='manager@example.com')
>>> managers_group = Group.objects.get(name='Managers')
>>> user.groups.add(managers_group)
>>> exit()

# 3. Проверить в UI: http://localhost:5000/users/management/
```

---

## Важные замечания

### Windows-специфичные особенности

1. **PowerShell vs CMD:** Все команды работают одинаково в обеих оболочках
2. **Кодировка:** Убедитесь, что терминал использует UTF-8:
   ```cmd
   chcp 65001
   ```
3. **Пути:** Django автоматически использует правильные разделители путей

### Логирование

Все важные события команд логируются в:
- **Консоль** — основной вывод команды
- **Лог-файл** — `logs/django.log` (если настроен)
- **База данных** — таблица `Attempt` (для send_mailing)

### Безопасность

- ⚠️ **Не используйте** эти команды в production без понимания их работы
- ⚠️ **Проверяйте** ID рассылки перед отправкой (особенно в production)
- ⚠️ **Бэкап** базы данных перед массовыми операциями

---

## Troubleshooting

### Проблема: "No module named 'apps'"

**Решение:**
```bash
# Убедитесь, что находитесь в корне проекта
cd /path/to/project
poetry run python manage.py <command>
```

### Проблема: "Database connection error"

**Решение:**
1. Проверьте `.env` файл (DB_NAME, DB_USER, DB_PASSWORD)
2. Убедитесь, что PostgreSQL запущен
3. Проверьте подключение:
   ```bash
   poetry run python manage.py check --database default
   ```

### Проблема: "Permission denied" при отправке email

**Решение:**
1. Проверьте настройки EMAIL в `.env`
2. Убедитесь, что SMTP-сервер доступен
3. Проверьте логи: `logs/django.log`

---

## Дополнительная информация

- **Django Management Commands:** https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- **Django-APScheduler:** Автоматический планировщик для отправки рассылок по расписанию
- **Run-Based Tracking:** Система партий/запусков для контролируемых повторных отправок

---

**Версия:** 1.0  
**Дата:** 2025-10-05  
**Проект:** Email Newsletter Management Service
