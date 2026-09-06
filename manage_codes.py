#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Управление кодами доступа для учеников
"""

import argparse
from database import Database
import string
import random

db = Database()


def generate_code(length=8):
    """Генерировать случайный код"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def create_codes(count: int, created_by: str = "admin"):
    """Создать коды доступа"""
    print(f"Создаю {count} кодов доступа...")

    codes = []
    for i in range(count):
        code = generate_code()
        codes.append((code, created_by))

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        for code, created_by in codes:
            cursor.execute(
                """
                INSERT INTO access_codes (code, created_by)
                VALUES (%s, %s)
                """,
                (code, created_by)
            )

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Создано {count} кодов:")
        for code, _ in codes:
            print(f"  - {code}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def list_codes(show_used=False):
    """Список кодов"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        if show_used:
            cursor.execute("SELECT code, is_used, used_at FROM access_codes ORDER BY created_at DESC")
            print("📋 Все коды:")
        else:
            cursor.execute("SELECT code, is_used FROM access_codes WHERE is_used = FALSE ORDER BY created_at DESC")
            print("📋 Неиспользованные коды:")

        codes = cursor.fetchall()

        if not codes:
            print("Нет кодов")
            return

        for code, is_used, *rest in codes:
            status = "✅ Использован" if is_used else "⏳ Активен"
            print(f"  {code} - {status}")

        cursor.close()
        conn.close()

        print(f"\nВсего: {len(codes)}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def delete_code(code: str):
    """Удалить код"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM access_codes WHERE code = %s", (code,))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"✅ Код {code} удалён")
        else:
            print(f"❌ Код {code} не найден")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    parser = argparse.ArgumentParser(description="Управление кодами доступа")
    subparsers = parser.add_subparsers(dest="command")

    # Создать коды
    create_parser = subparsers.add_parser("create", help="Создать коды")
    create_parser.add_argument("-n", "--number", type=int, default=10, help="Количество кодов")
    create_parser.add_argument("-b", "--by", default="admin", help="Кто создал")

    # Список кодов
    list_parser = subparsers.add_parser("list", help="Список кодов")
    list_parser.add_argument("-a", "--all", action="store_true", help="Показать все коды")

    # Удалить код
    delete_parser = subparsers.add_parser("delete", help="Удалить код")
    delete_parser.add_argument("code", help="Код для удаления")

    args = parser.parse_args()

    if args.command == "create":
        create_codes(args.number, args.by)
    elif args.command == "list":
        list_codes(args.all)
    elif args.command == "delete":
        delete_code(args.code)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
