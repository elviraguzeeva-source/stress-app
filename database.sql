-- Схема базы данных для приложения "Ударения на ЕГЭ"
-- PostgreSQL

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(255),
    is_student BOOLEAN DEFAULT FALSE,
    access_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Прогресс ученика
CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    section_id VARCHAR(50) NOT NULL,
    cards_completed INTEGER DEFAULT 0,
    total_cards INTEGER DEFAULT 0,
    test_passed BOOLEAN DEFAULT FALSE,
    test_score INTEGER DEFAULT 0,
    test_errors INTEGER DEFAULT 0,
    final_test_passed BOOLEAN DEFAULT FALSE,
    final_test_score INTEGER DEFAULT 0,
    final_test_errors INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'retake_needed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, section_id)
);

-- История ответов на тесты
CREATE TABLE IF NOT EXISTS test_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    section_id VARCHAR(50) NOT NULL,
    question_number INTEGER NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN,
    test_type VARCHAR(20) DEFAULT 'section', -- 'section' или 'final'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Коды доступа для учеников
CREATE TABLE IF NOT EXISTS access_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_by_user_id INTEGER REFERENCES users(id),
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP
);

-- Платежи
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL, -- в копейках
    reason VARCHAR(255), -- 'retake_failed', 'final_retake'
    payment_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'succeeded', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_section ON progress(user_id, section_id);
CREATE INDEX IF NOT EXISTS idx_test_answers_user ON test_answers(user_id);
CREATE INDEX IF NOT EXISTS idx_access_codes_code ON access_codes(code);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
