#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демо версия приложения без БД
"""

import json
from flask import Flask, jsonify, request, render_template
import os

app = Flask(__name__, template_folder='/home/claude/templates')

# Загружаем слова
with open('/home/claude/stress_words.json', 'r', encoding='utf-8') as f:
    STRESS_DATA = json.load(f)

# Данные в памяти (для демо)
demo_data = {}

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

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/auth/validate-code', methods=['POST'])
def validate_code():
    """Проверить код доступа"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    user_id = data.get('user_id')

    # Для демо - любой код работает
    if code and user_id:
        demo_data[user_id] = {'is_student': True}
        return jsonify({'valid': True, 'message': '✅ Код активирован! Добро пожаловать!'})
    else:
        return jsonify({'valid': False, 'error': 'Неверные параметры'}), 400

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
    import random

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

    if len(all_words) < 5:
        return jsonify({'error': 'Недостаточно слов'}), 400

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
            'correct_answers': []
        })

    return jsonify({
        'section_id': section_id,
        'total_questions': len(questions),
        'questions': questions
    })

@app.route('/api/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    """Получить прогресс пользователя"""
    return jsonify([])

@app.route('/api/progress/save', methods=['POST'])
def save_progress():
    """Сохранить прогресс"""
    return jsonify({'success': True})

@app.route('/api/final-test/submit', methods=['POST'])
def submit_final_test():
    """Отправить финальный тест"""
    data = request.get_json()
    errors = data.get('errors', 0)
    score = data.get('score', 0)

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

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════╗
║   📚 ДЕМО: Ударения на ЕГЭ                ║
║   🚀 Сервер запускается...                 ║
║   🌐 Откройте: http://localhost:5000      ║
║   💡 Код доступа для тестирования: test123║
╚════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)
