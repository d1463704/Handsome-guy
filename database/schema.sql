DROP TABLE IF EXISTS reminders;
DROP TABLE IF EXISTS status_records;
DROP TABLE IF EXISTS user_bindings;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK(role IN ('elder', 'family')),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    phone TEXT,
    elder_code TEXT UNIQUE
);

CREATE TABLE user_bindings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    elder_id INTEGER NOT NULL,
    FOREIGN KEY (family_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(family_id, elder_id)
);

CREATE TABLE status_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elder_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('CHECKIN', 'SOS')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    elder_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    title TEXT NOT NULL,
    remind_time TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
);
