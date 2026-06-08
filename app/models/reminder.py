"""
提醒事項模型 — 管理用藥、回診等提醒
"""
import sqlite3
from .db import get_db_connection


def create(data):
    """新增一筆提醒事項"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reminders (elder_id, created_by, title, remind_time, is_active) VALUES (?, ?, ?, ?, 1)",
            (data.get('elder_id'), data.get('created_by'), data.get('title'), data.get('remind_time')))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in reminder.create: {e}")
        return None
    finally:
        conn.close()


def get_all():
    """取得所有提醒事項"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM reminders").fetchall()
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_all: {e}")
        return []
    finally:
        conn.close()


def get_by_id(reminder_id):
    """取得單筆提醒事項"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_by_id: {e}")
        return None
    finally:
        conn.close()


def update(reminder_id, data):
    """更新提醒事項內容"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE reminders SET title = ?, remind_time = ?, is_active = ? WHERE id = ?",
            (data.get('title'), data.get('remind_time'), data.get('is_active', 1), reminder_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in reminder.update: {e}")
        return False
    finally:
        conn.close()


def delete(reminder_id):
    """刪除提醒事項"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in reminder.delete: {e}")
        return False
    finally:
        conn.close()


def get_reminders_by_elder(elder_id, active_only=True):
    """取得特定長者的提醒事項"""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM reminders WHERE elder_id = ?"
        params = [elder_id]
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY remind_time ASC"
        return conn.execute(query, tuple(params)).fetchall()
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_reminders_by_elder: {e}")
        return []
    finally:
        conn.close()


def update_status(reminder_id, is_active):
    """單純更新提醒事項啟用狀態"""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE reminders SET is_active = ? WHERE id = ?", (is_active, reminder_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in reminder.update_status: {e}")
        return False
    finally:
        conn.close()
