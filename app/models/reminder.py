from .db import get_db_connection

def create_reminder(elder_id, created_by, title, remind_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reminders (elder_id, created_by, title, remind_time, is_active) "
            "VALUES (?, ?, ?, ?, 1)",
            (elder_id, created_by, title, remind_time)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_reminders_by_elder(elder_id, active_only=True):
    conn = get_db_connection()
    query = "SELECT * FROM reminders WHERE elder_id = ?"
    params = [elder_id]
    
    if active_only:
        query += " AND is_active = 1"
        
    query += " ORDER BY remind_time ASC"
    
    reminders = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return reminders

def update_reminder_status(reminder_id, is_active):
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE reminders SET is_active = ? WHERE id = ?",
            (is_active, reminder_id)
        )
        conn.commit()
    finally:
        conn.close()

def delete_reminder(reminder_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
    finally:
        conn.close()
