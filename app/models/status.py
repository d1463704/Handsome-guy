from .db import get_db_connection
from datetime import datetime

def create_status_record(elder_id, record_type):
    """新增狀態紀錄 (CHECKIN 或 SOS)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO status_records (elder_id, type) VALUES (?, ?)",
            (elder_id, record_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_records_by_elder(elder_id, limit=50):
    """取得長者的所有狀態紀錄，預設回傳最新 50 筆"""
    conn = get_db_connection()
    records = conn.execute(
        "SELECT * FROM status_records WHERE elder_id = ? ORDER BY created_at DESC LIMIT ?",
        (elder_id, limit)
    ).fetchall()
    conn.close()
    return records

def get_today_checkin(elder_id):
    """檢查長者今天是否已經平安打卡"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    record = conn.execute(
        "SELECT * FROM status_records "
        "WHERE elder_id = ? AND type = 'CHECKIN' AND date(created_at) = date(?)",
        (elder_id, today_date)
    ).fetchone()
    conn.close()
    return record
