# 🚀 Развертывание на Railway — Пошаговая инструкция

## Этап 1: Подготовка GitHub репозитория

### 1.1 Создать репозиторий на GitHub

1. Перейди на [github.com](https://github.com)
2. Создай новый репозиторий `stress-app`
3. Клонируй на компьютер

### 1.2 Загрузить файлы проекта

```bash
# В папке проекта
git add .
git commit -m "Initial commit: Telegram app for stress learning"
git branch -M main
git remote add origin https://github.com/your-username/stress-app.git
git push -u origin main
```

## Этап 2: Railway Настройка

### 2.1 Регистрация на Railway

1. Перейди на [railway.app](https://railway.app)
2. Зарегистрируйся через GitHub (рекомендуется)
3. Создай новый проект

### 2.2 Добавь PostgreSQL базу данных

1. В Railway нажми "+ New"
2. Выбери "Database"
3. Выбери "PostgreSQL"
4. Дождись инициализации

### 2.3 Выполни SQL скрипт

1. Открой Database в Railway
2. Нажми на "PostgreSQL" → "Query"
3. Скопируй содержимое `database.sql`
4. Вставь и выполни запрос

Результат:
```
✅ Users table created
✅ Progress table created
✅ All tables initialized
```

### 2.4 Добавь приложение

1. В Railway нажми "+ New"
2. Выбери "GitHub Repo"
3. Выбери `stress-app`

### 2.5 Установи переменные окружения

1. В приложении нажми на "Variables"
2. Добавь переменные:

| Переменная | Значение | Примечание |
|-----------|---------|-----------|
| `TELEGRAM_BOT_TOKEN` | Получи у @BotFather | Обязательно |
| `WEB_APP_URL` | `https://stress-app-prod.railway.app` | Будет позже |
| `PORT` | `5000` | По умолчанию |
| `FLASK_ENV` | `production` | Для prod |
| `DATABASE_URL` | Автоматически из Postgres | Проверь в Postgres |

**Получить `DATABASE_URL`:**
1. Открой "PostgreSQL" → "Connect"
2. Копируй "Postgres Connection" (URL)
3. Вставь в `DATABASE_URL`

### 2.6 Запустить развертывание

1. Railway автоматически заметит изменения в GitHub
2. Начнёт процесс сборки (~ 2 минуты)
3. Когда статус станет "✅ Running" — готово!

**Копируй URL приложения**, он будет нужен для бота

## Этап 3: Telegram Bot

### 3.1 Получить токен

1. Открой Telegram
2. Найди **@BotFather**
3. Отправь `/newbot`
4. Следуй инструкциям:
   - Название: "Ударения на ЕГЭ"
   - Юзернейм: `@stress_app_bot` (или свой)
5. Скопируй токен (очень длинная строка)
6. Вставь в Railway `TELEGRAM_BOT_TOKEN`

### 3.2 Обновить `WEB_APP_URL` в Railway

1. Скопируй URL приложения из Railway
2. В Railway переменные обнови:
   ```
   WEB_APP_URL=https://your-app-url.railway.app
   ```
3. Приложение перезагрузится

### 3.3 Запустить вебхук (для production)

Когда приложение работает, выполни в терминале:

```bash
curl -X POST https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app-url.railway.app/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'
```

Результат:
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

## Этап 4: Создание кодов доступа для учеников

### 4.1 Локально создать коды

```bash
python manage_codes.py create -n 20 -b "Эльвира"
```

Результат:
```
Создаю 20 кодов доступа...
✅ Создано 20 кодов:
  - ABC123XY
  - DEF456ZW
  ...
```

### 4.2 Загрузить коды в базу Railway

Есть два способа:

**Способ 1: Через Query (PostgreSQL in Railway)**
```sql
INSERT INTO access_codes (code, created_by) VALUES 
  ('ABC123XY', 'Эльвира'),
  ('DEF456ZW', 'Эльвира'),
  ('GHI789PQ', 'Эльвира');
```

**Способ 2: Через Railway CLI**
```bash
# Установи Railway CLI
npm i -g @railway/cli

# Логин в Railway
railway login

# Выбери проект
railway link

# Выполни SQL
railway database query < insert_codes.sql
```

## Этап 5: Тестирование

### 5.1 Отправить сообщение боту

1. Открой Telegram
2. Найди своего бота `@stress_app_bot`
3. Нажми "Start" или напиши `/start`

**Ожидаемый результат:**
```
👋 Привет!
Я помогу тебе запомнить ударения для ЕГЭ...
[Кнопка] 📖 Начать обучение
```

### 5.2 Нажать на кнопку

Откроется Web App с интерфейсом приложения

**Ожидаемый результат:**
```
📚 Ударения
Подготовка к ЕГЭ по русскому

[Таб] Студент | Гость
[Поле] Код доступа
[Кнопка] Активировать
```

### 5.3 Ввести код доступа

```
Код: ABC123XY
Нажми "Активировать"
```

**Ожидаемый результат:**
```
✅ Код активирован!

📖 Выбери раздел
- Ударение в существительных множественного числа
- Е или Ё
- Ударение в словах женского рода
...
```

### 5.4 Пройти обучение

1. Выбери раздел
2. Учи слова на карточках (по 3-4 слова)
3. Проходи тесты
4. Смотри результаты

## Этап 6: Production настройка

### 6.1 Включить Auto-Deploy

1. В Railway → Settings
2. Включи "Auto Deploy on Push"
3. Теперь любой push в `main` автоматически развернёт

### 6.2 Мониторинг

В Railway можно смотреть:
- **Logs**: Ошибки и логи приложения
- **Metrics**: CPU, Memory, Network
- **Database**: Статистика БД

### 6.3 Резервная копия БД

```bash
# Скачать backup (через Railway CLI)
railway database backup

# Или через pg_dump
pg_dump -U postgres -h <host> -d stress_app > backup.sql
```

## Этап 7: Домен (опционально)

Если хочешь свой домен вместо `railway.app`:

1. Купи домен (GoDaddy, Namecheap и т.д.)
2. В Railway → Settings → Domain
3. Добавь свой домен
4. Следуй инструкциям по DNS

## Частые ошибки и решения

### ❌ "Не удалось подключиться к БД"

**Решение:**
- Проверь `DATABASE_URL` в Railway
- Убедись, что PostgreSQL запущен
- Выполни SQL скрипт заново

### ❌ "Webhook failed"

**Решение:**
```bash
# Проверь текущий webhook
curl https://api.telegram.org/bot<ТОКЕН>/getWebhookInfo

# Переустанови webhook
curl -X POST https://api.telegram.org/bot<ТОКЕН>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-url.railway.app/webhook"}'
```

### ❌ "Приложение не запускается (Build Failed)"

**Решение:**
- Проверь `requirements.txt` — все ли пакеты там
- Проверь Logs в Railway
- Убедись, что Python версия >= 3.8

### ❌ "Код не работает (Permission Denied)"

**Решение:**
- Убедись, что коды добавлены в таблицу `access_codes`
- Проверь спеллинг кода
- Запрос LOG базе: `SELECT * FROM access_codes LIMIT 5;`

## 📞 Поддержка

Если что-то не работает:

1. **Проверь Logs в Railway** (Deployments → Logs)
2. **Смотри Database Query результаты**
3. **Напиши в Telegram support**

---

**Готово! 🎉** 

Теперь тебе нужно:
1. ✅ Поделиться ссылкой на бота с учениками
2. ✅ Дать им коды доступа
3. ✅ Зарабатывать! 💰

Каждый платный доступ = 299 ₽
