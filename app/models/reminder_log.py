"""
提醒紀錄與討論串模型 — 記錄每日提醒完成狀態與相關留言
"""
import sqlite3
from .db import get_db_connection
from datetime import datetime, date

def log_reply(reminder_id, elder_id, status):
    """
    新增或更新今日的提醒狀態紀錄
    如果今日已有紀錄，則更新；否則新增
    """
    conn = get_db_connection()
    try:
        today_start = date.today().strftime('%Y-%m-%d 00:00:00')
        today_end = date.today().strftime('%Y-%m-%d 23:59:59')
        
        # 檢查今日是否已有紀錄
        cursor = conn.execute(
            "SELECT id FROM reminder_logs WHERE reminder_id = ? AND created_at BETWEEN ? AND ?",
            (reminder_id, today_start, today_end)
        )
        existing = cursor.fetchone()
        
        if existing:
            conn.execute(
                "UPDATE reminder_logs SET status = ? WHERE id = ?",
                (status, existing['id'])
            )
            log_id = existing['id']
        else:
            cursor = conn.execute(
                "INSERT INTO reminder_logs (reminder_id, elder_id, status) VALUES (?, ?, ?)",
                (reminder_id, elder_id, status)
            )
            log_id = cursor.lastrowid
            
        conn.commit()
        return log_id
    except sqlite3.Error as e:
        print(f"Database error in reminder_log.log_reply: {e}")
        return None
    finally:
        conn.close()


def get_today_logs_by_elder(elder_id):
    """取得特定長者今日的所有提醒紀錄 (包含回覆狀態)"""
    conn = get_db_connection()
    try:
        today_start = date.today().strftime('%Y-%m-%d 00:00:00')
        today_end = date.today().strftime('%Y-%m-%d 23:59:59')
        
        logs = conn.execute(
            "SELECT * FROM reminder_logs WHERE elder_id = ? AND created_at BETWEEN ? AND ?",
            (elder_id, today_start, today_end)
        ).fetchall()
        
        return {log['reminder_id']: dict(log) for log in logs}
    except sqlite3.Error as e:
        print(f"Database error in reminder_log.get_today_logs_by_elder: {e}")
        return {}
    finally:
        conn.close()


def add_comment(log_id, sender_id, message):
    """新增討論串留言"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO reminder_comments (log_id, sender_id, message) VALUES (?, ?, ?)",
            (log_id, sender_id, message)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in reminder_log.add_comment: {e}")
        return None
    finally:
        conn.close()


def get_comments_by_log(log_id):
    """取得特定提醒紀錄的所有留言，並關聯發送者資訊"""
    conn = get_db_connection()
    try:
        query = '''
            SELECT c.*, u.display_name, u.role
            FROM reminder_comments c
            JOIN users u ON c.sender_id = u.id
            WHERE c.log_id = ?
            ORDER BY c.created_at ASC
        '''
        comments = conn.execute(query, (log_id,)).fetchall()
        
        result = []
        for c in comments:
            c_dict = dict(c)
            # 轉換時間格式使其更友善 (例如: 14:30)
            try:
                dt = datetime.strptime(c_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                c_dict['time_str'] = dt.strftime('%H:%M')
            except:
                c_dict['time_str'] = c_dict['created_at']
            result.append(c_dict)
            
        return result
    except sqlite3.Error as e:
        print(f"Database error in reminder_log.get_comments_by_log: {e}")
        return []
    finally:
        conn.close()


def get_today_logs_with_comments_by_elder(elder_id):
    """取得特定長者今日的所有提醒紀錄及留言，供儀表板顯示用"""
    conn = get_db_connection()
    try:
        today_start = date.today().strftime('%Y-%m-%d 00:00:00')
        today_end = date.today().strftime('%Y-%m-%d 23:59:59')
        
        logs = conn.execute(
            "SELECT * FROM reminder_logs WHERE elder_id = ? AND created_at BETWEEN ? AND ?",
            (elder_id, today_start, today_end)
        ).fetchall()
        
        result = {}
        for log in logs:
            log_dict = dict(log)
            log_dict['comments'] = get_comments_by_log(log['id'])
            result[log['reminder_id']] = log_dict
            
        return result
    except sqlite3.Error as e:
        print(f"Database error in reminder_log.get_today_logs_with_comments: {e}")
        return {}
    finally:
        conn.close()
