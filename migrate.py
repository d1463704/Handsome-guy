import sqlite3

def upgrade():
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Create reminder_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminder_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_id INTEGER NOT NULL,
            elder_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('completed', 'difficult')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reminder_id) REFERENCES reminders (id) ON DELETE CASCADE,
            FOREIGN KEY (elder_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Create reminder_comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminder_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (log_id) REFERENCES reminder_logs (id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully.")

if __name__ == '__main__':
    upgrade()
