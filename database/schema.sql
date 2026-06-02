-- 獨居老人生活管家 資料庫 Schema
-- SQLite 語法

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK(role IN ('elder', 'family')),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    phone TEXT,
    elder_code TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS user_bindings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    elder_id INTEGER NOT NULL,
    FOREIGN KEY (family_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(family_id, elder_id)
);

-- mood_score: 1~5 分，NULL 表示未填寫
CREATE TABLE IF NOT EXISTS status_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elder_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('CHECKIN', 'SOS')),
    mood_score INTEGER CHECK(mood_score BETWEEN 1 AND 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elder_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    title TEXT NOT NULL,
    remind_time TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
);
