#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Работа с базой данных PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с БД"""

    def __init__(self):
        self.conn_string = os.getenv('DATABASE_URL')

    def get_connection(self):
        """Получить соединение"""
        return psycopg2.connect(self.conn_string)

    def add_user(self, telegram_id: int, first_name: str) -> int:
        """Добавить нового пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (telegram_id, first_name)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id) DO UPDATE
                SET updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (telegram_id, first_name)
            )

            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return user_id

        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return None

    def get_user_by_telegram_id(self, telegram_id: int):
        """Получить пользователя по Telegram ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            return user

        except Exception as e:
            logger.error(f"Ошибка при получении пользователя: {e}")
            return None

    def validate_access_code(self, code: str) -> bool:
        """Проверить код доступа"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT is_used FROM access_codes WHERE code = %s",
                (code,)
            )

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return result and not result[0]

        except Exception as e:
            logger.error(f"Ошибка при проверке кода: {e}")
            return False

    def use_access_code(self, code: str, user_id: int) -> bool:
        """Использовать код доступа"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE access_codes
                SET is_used = TRUE, used_by_user_id = %s, used_at = CURRENT_TIMESTAMP
                WHERE code = %s AND is_used = FALSE
                """,
                (user_id, code)
            )

            updated = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()

            return updated

        except Exception as e:
            logger.error(f"Ошибка при использовании кода: {e}")
            return False

    def mark_student(self, user_id: int) -> bool:
        """Отметить как студента"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET is_student = TRUE WHERE id = %s",
                (user_id,)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Ошибка при отметке студента: {e}")
            return False

    def save_progress(self, user_id: int, section_id: str, data: dict) -> bool:
        """Сохранить прогресс"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO progress (user_id, section_id, cards_completed, total_cards, test_passed, test_score, test_errors, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, section_id) DO UPDATE
                SET
                    cards_completed = EXCLUDED.cards_completed,
                    total_cards = EXCLUDED.total_cards,
                    test_passed = EXCLUDED.test_passed,
                    test_score = EXCLUDED.test_score,
                    test_errors = EXCLUDED.test_errors,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    user_id,
                    section_id,
                    data.get('cards_completed', 0),
                    data.get('total_cards', 0),
                    data.get('test_passed', False),
                    data.get('test_score', 0),
                    data.get('test_errors', 0),
                    data.get('status', 'in_progress')
                )
            )

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении прогресса: {e}")
            return False

    def get_user_progress(self, user_id: int):
        """Получить весь прогресс пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                "SELECT * FROM progress WHERE user_id = %s ORDER BY section_id",
                (user_id,)
            )

            progress = cursor.fetchall()
            cursor.close()
            conn.close()

            return progress

        except Exception as e:
            logger.error(f"Ошибка при получении прогресса: {e}")
            return []

    def save_final_test(self, user_id: int, score: int, errors: int) -> bool:
        """Сохранить финальный тест"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Обновим все разделы со статусом
            cursor.execute(
                """
                UPDATE progress
                SET final_test_passed = (%s = 0), final_test_score = %s, final_test_errors = %s, status = 'completed'
                WHERE user_id = %s
                """,
                (errors, score, errors, user_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении финального теста: {e}")
            return False

    def create_payment(self, user_id: int, amount: int, reason: str) -> dict:
        """Создать запись о платеже"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                INSERT INTO payments (user_id, amount, reason, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING id, payment_id
                """,
                (user_id, amount, reason)
            )

            payment = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            return payment

        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return None
