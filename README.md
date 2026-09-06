# 📚 Ударения на ЕГЭ — Telegram приложение

Интерактивное приложение для запоминания ударений в словах, необходимых для ЕГЭ по русскому языку.

## 🎯 Особенности

- ✅ Карточки для изучения (по 3-4 слова с логикой)
- ✅ Тесты в формате ЕГЭ (5 заданий)
- ✅ Финальное тестирование (30 заданий)
- ✅ Система оценивания и отслеживание прогресса
- ✅ Бесплатный доступ для учеников Эльвиры (по кодам)
- ✅ Платный доступ для остальных (299 ₽)
- ✅ Интеграция с YooKassa для платежей

## 🏗️ Архитектура

```
┌─────────────────────────────────────────┐
│        Telegram Bot (@your_bot)        │
│  (python-telegram-bot, Railway)        │
└────────────────┬────────────────────────┘
                 │ Web App URL
                 ▼
┌─────────────────────────────────────────┐
│        Web App (Flask)                   │
│  (Карточки, Тесты, Результаты)         │
│  (Railway)                              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   PostgreSQL Database                   │
│   (Railway Postgres)                    │
└─────────────────────────────────────────┘
```

## 🚀 Развертывание на Railway

### 1. Подготовка репозитория

```bash
# Клонируй проект
git clone <repo-url>
cd stress-app

# Инициализируй Git (если нужно)
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. На Railway

1. **Создай новый проект**: [railway.app](https://railway.app)
2. **Добавь базу данных PostgreSQL**:
   - Создай переменную `DATABASE_URL` с подключением
   - Скопируй SQL из `database.sql` и выполни в bastion/query
3. **Добавь переменные окружения**:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   WEB_APP_URL=https://<your-app>.railway.app
   ```
4. **Развой приложение**:
   - Привяжи GitHub репозиторий
   - Railway автоматически установит зависимости из `requirements.txt`
   - Запустит процессы из `Procfile`

### 3. Telegram Bot

1. **Получи токен**:
   - Напиши @BotFather в Telegram
   - Команда `/newbot`
   - Сохрани токен в переменной `TELEGRAM_BOT_TOKEN`

2. **Установи webhook** (для prod):
   ```bash
   curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://<your-app>.railway.app/webhook",
       "allowed_updates": ["message", "callback_query"]
     }'
   ```

### 4. Коды доступа для учеников

```bash
# В базе данных выполни:
INSERT INTO access_codes (code, created_by) VALUES 
  ('CODE123', 'Эльвира'),
  ('CODE456', 'Эльвира'),
  ('CODE789', 'Эльвира');
```

## 📝 Структура проекта

```
.
├── bot.py                   # Telegram бот
├── app.py                   # Flask приложение
├── database.py              # Работа с БД
├── stress_data.py           # Парсер данных
├── stress_words.json        # Список слов по разделам
├── database.sql             # Схема БД
├── requirements.txt         # Зависимости Python
├── Procfile                 # Конфигурация для Railway
├── .env.example             # Пример переменных окружения
└── templates/
    └── index.html           # Web App интерфейс
```

## 🔧 Локальная разработка

```bash
# 1. Установи зависимости
pip install -r requirements.txt

# 2. Создай .env файл
cp .env.example .env
# Заполни значения в .env

# 3. Инициализируй БД
psql -U postgres -d stress_app -f database.sql

# 4. Запусти приложение
python app.py

# 5. В другом терминале запусти бот
python bot.py
```

## 📊 API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|---------|
| `/api/auth/validate-code` | POST | Валидировать код доступа |
| `/api/data/sections` | GET | Список разделов |
| `/api/data/section/<id>` | GET | Данные раздела с карточками |
| `/api/data/section/<id>/test` | GET | Тестовые вопросы |
| `/api/progress/<user_id>` | GET | Прогресс пользователя |
| `/api/progress/save` | POST | Сохранить прогресс |
| `/api/final-test/submit` | POST | Отправить финальный тест |
| `/api/payment/create` | POST | Создать платёж |

## 💳 Платежи (YooKassa)

TODO: Интегрировать YooKassa API

```python
# Пример в app.py:
# - Создать платёж
# - Получить ссылку на оплату
# - Проверить статус платежа
```

## 📱 Как пользователь будет использовать

1. **Открыть бота**: @your_bot_username
2. **Нажать кнопку**: "Начать обучение"
3. **Открыется Web App** с интерфейсом
4. **Если студент**: ввести код доступа
5. **Если нет**: оплатить доступ
6. **Учить слова**: карточки → тесты → финальное тестирование

## ⚙️ Конфигурация

### Размер порций слов
В `app.py` функция `split_into_cards()`:
```python
cards_per_word = 3  # Слов на карточку
```

### Оценивание
В `app.py` функция `submit_final_test()`:
- 0 ошибок = 5 баллов
- 1-3 ошибки = 4 балла
- 4-7 ошибок = 3 балла (повторение за 299 ₽)
- >7 ошибок = учить заново

### Цена
- Доступ: 299 ₽
- Повторение после 3 баллов: 299 ₽

## 📞 Поддержка

Для вопросов свяжитесь с Эльвирой:
- Telegram: @ruslit_online
- Instagram: @ruslit_online
- WhatsApp: [ссылка из документа]

## 📄 Лицензия

Создано для Эльвиры Гузеевой, репетитора по русскому языку.
