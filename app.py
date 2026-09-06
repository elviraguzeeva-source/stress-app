#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask приложение для Web App
"""

import os
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import Database
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# БД
db = Database()

# Загружаем слова
with open('stress_words.json', 'r', encoding='utf-8') as f:
    STRESS_DATA = json.load(f)


def split_into_cards(words: list, cards_per_word: int = 3) -> list:
    """Разбить слова на карточки по 3-4 слова"""
    cards = []
    for i in range(0, len(words), cards_per_word):
        card_words = words[i:i+cards_per_word]
        cards.append({
            'words': card_words,
            'number': len(cards) + 1
        })
    return cards


def get_test_questions(section_id: str, exclude_word_indices: set = None) -> list:
    """Получить 5 тестовых заданий для раздела"""
    import random

    # Найдём раздел
    section = None
    for s in STRESS_DATA['sections']:
        if s['id'] == section_id:
            section = s
            break

    if not section:
        return []

    # Соберём все слова из раздела
    all_words = []
    for sub in section['subsections']:
        all_words.extend(sub.get('words', []))

    if len(all_words) < 5:
        return []

    # Создадим 5 вопросов
    questions = []
    for q_num in range(5):
        # Выбираем 5 слов для вопроса
        selected_words = random.sample(all_words, min(5, len(all_words)))

        questions.append({
            'number': q_num + 1,
            'type': 'select_incorrect_stress',
            'text': 'Укажите слово(-а) с неправильным ударением:',
            'words': selected_words,
            'correct_answers': []  # На клиенте будет проверяться
        })

    return questions


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/auth/validate-code', methods=['POST'])
def validate_code():
    """Проверить код доступа"""
    data = request.get_json()
    code = data.get('code', '').strip()
    user_id = data.get('user_id')

    if not code or not user_id:
        return jsonify({'valid': False, 'error': 'Неверные параметры'}), 400

    if db.validate_access_code(code):
        # Используем код
        if db.use_access_code(code, user_id):
            db.mark_student(user_id)
            return jsonify({'valid': True, 'message': 'Код активирован! Добро пожаловать!'})
        else:
            return jsonify({'valid': False, 'error': 'Ошибка при активации кода'}), 400
    else:
        return jsonify({'valid': False, 'error': 'Код неверный или уже использован'}), 400


@app.route('/api/data/sections', methods=['GET'])
def get_sections():
    """Получить список разделов"""
    sections = []
    for section in STRESS_DATA['sections']:
        sections.append({
            'id': section['id'],
            'name': section['name'],
            'subsection_count': len(section['subsections'])
        })
    return jsonify(sections)


@app.route('/api/data/section/<section_id>', methods=['GET'])
def get_section(section_id):
    """Получить раздел со словами и карточками"""
    section = None
    for s in STRESS_DATA['sections']:
        if s['id'] == section_id:
            section = s
            break

    if not section:
        return jsonify({'error': 'Раздел не найден'}), 404

    # Соберём все слова из раздела
    all_words = []
    for sub in section['subsections']:
        all_words.extend(sub.get('words', []))

    # Разбиваем на карточки
    cards = split_into_cards(all_words)

    return jsonify({
        'id': section['id'],
        'name': section['name'],
        'total_words': len(all_words),
        'total_cards': len(cards),
        'cards': cards
    })


@app.route('/api/data/section/<section_id>/test', methods=['GET'])
def get_section_test(section_id):
    """Получить тест для раздела"""
    questions = get_test_questions(section_id)

    if not questions:
        return jsonify({'error': 'Не удалось создать тест'}), 400

    return jsonify({
        'section_id': section_id,
        'total_questions': len(questions),
        'questions': questions
    })


@app.route('/api/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    """Получить прогресс пользователя"""
    progress = db.get_user_progress(user_id)
    return jsonify(progress or [])


@app.route('/api/progress/save', methods=['POST'])
def save_progress():
    """Сохранить прогресс"""
    data = request.get_json()
    user_id = data.get('user_id')
    section_id = data.get('section_id')
    progress_data = data.get('progress', {})

    if not user_id or not section_id:
        return jsonify({'error': 'Неверные параметры'}), 400

    if db.save_progress(user_id, section_id, progress_data):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Ошибка при сохранении'}), 500


@app.route('/api/final-test/submit', methods=['POST'])
def submit_final_test():
    """Отправить финальный тест"""
    data = request.get_json()
    user_id = data.get('user_id')
    score = data.get('score', 0)
    errors = data.get('errors', 0)

    if not user_id:
        return jsonify({'error': 'Неверные параметры'}), 400

    if db.save_final_test(user_id, score, errors):
        # Определяем оценку
        if errors == 0:
            rating = 5
            message = "🌟 Отлично! Ты выучил все слова!"
        elif 1 <= errors <= 3:
            rating = 4
            message = "👍 Хорошо! Повтори немного материала."
        elif 4 <= errors <= 7:
            rating = 3
            message = "⏰ Нужно ещё потренироваться. Хочешь повторить за 299 рублей?"
        else:
            rating = 2
            message = "📚 Учи заново. Повторение доступно за 299 рублей."

        return jsonify({
            'success': True,
            'rating': rating,
            'message': message,
            'score': score,
            'errors': errors
        })
    else:
        return jsonify({'error': 'Ошибка при сохранении результата'}), 500


@app.route('/api/payment/create', methods=['POST'])
def create_payment():
    """Создать платёж"""
    data = request.get_json()
    user_id = data.get('user_id')
    reason = data.get('reason', 'unknown')  # 'retake_failed', 'final_retake'

    if not user_id:
        return jsonify({'error': 'Неверные параметры'}), 400

    # Сумма: 299 рублей = 29900 копеек
    amount = 29900

    payment = db.create_payment(user_id, amount, reason)

    if payment:
        # TODO: Интегрировать YooKassa для реального платежа
        return jsonify({
            'success': True,
            'payment_id': payment.get('id'),
            'amount': amount
        })
    else:
        return jsonify({'error': 'Ошибка при создании платежа'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья приложения"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
