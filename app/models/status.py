import sqlite3
from .db import get_db_connection
from datetime import datetime

def create(data):
    """新增狀態紀錄 (CHECKIN 或 SOS)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO status_records (elder_id, type) VALUES (?, ?)",
            (data.get('elder_id'), data.get('type'))
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in status.create: {e}")
        return None
    finally:
        conn.close()

def get_all():
    """取得系統中所有打卡紀錄"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM status_records ORDER BY created_at DESC").fetchall()
    except sqlite3.Error as e:
        print(f"Database error in status.get_all: {e}")
        return []
    finally:
        conn.close()

def get_by_id(record_id):
    """取得單筆紀錄"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM status_records WHERE id = ?", (record_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in status.get_by_id: {e}")
        return None
    finally:
        conn.close()

def update(record_id, data):
    """更新紀錄 (通常不會用到，為了符合標準實作)"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE status_records SET type = ? WHERE id = ?",
            (data.get('type'), record_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in status.update: {e}")
        return False
    finally:
        conn.close()

def delete(record_id):
    """刪除紀錄"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM status_records WHERE id = ?", (record_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in status.delete: {e}")
        return False
    finally:
        conn.close()

def get_records_by_elder(elder_id, limit=50):
    """取得特定長者的所有紀錄"""
    conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM status_records WHERE elder_id = ? ORDER BY created_at DESC LIMIT ?",
            (elder_id, limit)
        ).fetchall()
    except sqlite3.Error as e:
        print(f"Database error in status.get_records_by_elder: {e}")
        return []
    finally:
        conn.close()

def get_today_checkin(elder_id):
    """檢查長者今天是否已經平安打卡"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM status_records WHERE elder_id = ? AND type = 'CHECKIN' AND date(created_at) = date(?)",
            (elder_id, today_date)
        ).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in status.get_today_checkin: {e}")
        return None
    finally:
        conn.close()
