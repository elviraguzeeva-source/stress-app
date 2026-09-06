#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для запоминания ударений - главный файл
"""

import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database import Database

# Загружаем переменные окружения
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://your-app.com')

# Инициализируем БД
db = Database()

# Загружаем данные со словами
with open('stress_words.json', 'r', encoding='utf-8') as f:
    STRESS_DATA = json.load(f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    user = update.effective_user

    # Добавляем пользователя в БД
    db.add_user(user.id, user.first_name)

    welcome_text = f"""
👋 Привет, {user.first_name}!

Я помогу тебе запомнить ударения для ЕГЭ по русскому языку.

Как это работает:
📚 Карточки для изучения (по 3-4 слова)
📝 Тесты в формате ЕГЭ (5 заданий)
🏆 Финальное тестирование (30 заданий)
⭐ Система оценивания

👨‍🎓 Если ты ученик Эльвиры — используй код доступа
💳 Если нет — оплати доступ через приложение

Нажми кнопку ниже, чтобы начать!
    """

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # Кнопка для открытия Web App
    keyboard = [
        [InlineKeyboardButton(
            "📖 Начать обучение",
            web_app=WebAppInfo(url=f"{WEB_APP_URL}/app?user_id={user.id}")
        )],
        [InlineKeyboardButton("❓ О приложении", callback_data="about")],
        [InlineKeyboardButton("⚙️ Помощь", callback_data="help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатия кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        about_text = """
ℹ️ *Об приложении*

Это интерактивное приложение для запоминания правильного ударения в словах, нужных для ЕГЭ по русскому языку.

✨ Особенности:
• Слова разделены по логическим группам
• Карточки для визуального запоминания
• Реальные тесты в формате ЕГЭ
• Отслеживание прогресса
• Система повторения для закрепления

💰 Стоимость доступа: 299 рублей (с повторениями)

Вопросы? Напиши Эльвире!
        """
        await query.edit_message_text(about_text, parse_mode=ParseMode.MARKDOWN)

    elif query.data == "help":
        help_text = """
❓ *Часто задаваемые вопросы*

*Как использовать приложение?*
1. Учи слова на карточках
2. Проходи тесты
3. Если результат хороший — переходи к следующему разделу
4. После всех разделов — финальное тестирование

*Что означают оценки?*
🟢 5 баллов — 0 ошибок (отлично!)
🟡 4 балла — 1-3 ошибки (хорошо)
🔴 3 балла — 4-7 ошибок (нужно ещё тренироваться)
⚫ Меньше 3 баллов — нужно учить заново

Вопросы? Напиши Эльвире в Telegram!
        """
        await query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ошибок"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Главная функция"""

    # Создаём Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бот
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
