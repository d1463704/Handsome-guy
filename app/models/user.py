"""
使用者模型 — 帳號的建立、查詢、綁定操作
"""
import sqlite3
import random
import string
from .db import get_db_connection


def create(data):
    """新增一筆使用者記錄"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (role, username, password_hash, display_name, phone, elder_code) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (data.get('role'), data.get('username'), data.get('password_hash'),
             data.get('display_name'), data.get('phone'), data.get('elder_code')))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in user.create: {e}")
        return None
    finally:
        conn.close()


def get_all():
    """取得所有使用者記錄"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM users").fetchall()
    except sqlite3.Error as e:
        print(f"Database error in user.get_all: {e}")
        return []
    finally:
        conn.close()


def get_by_id(user_id):
    """取得單筆使用者記錄"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in user.get_by_id: {e}")
        return None
    finally:
        conn.close()


def update(user_id, data):
    """更新使用者記錄"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE users SET display_name = ?, phone = ? WHERE id = ?",
            (data.get('display_name'), data.get('phone'), user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in user.update: {e}")
        return False
    finally:
        conn.close()


def delete(user_id):
    """刪除使用者記錄"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error in user.delete: {e}")
        return False
    finally:
        conn.close()


def get_user_by_username(username):
    """透過帳號取得使用者"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in user.get_user_by_username: {e}")
        return None
    finally:
        conn.close()


def get_user_by_elder_code(elder_code):
    """透過綁定碼取得長者"""
    conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE elder_code = ? AND role = 'elder'", (elder_code,)
        ).fetchone()
    except sqlite3.Error as e:
        print(f"Database error in user.get_user_by_elder_code: {e}")
        return None
    finally:
        conn.close()


def bind_elder_to_family(family_id, elder_id):
    """綁定長者與家屬"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_bindings (family_id, elder_id) VALUES (?, ?)",
            (family_id, elder_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        print(f"Database error in user.bind_elder_to_family: {e}")
        return False
    finally:
        conn.close()


def get_bound_elders(family_id):
    """取得家屬綁定的所有長者"""
    conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT u.* FROM users u JOIN user_bindings b ON u.id = b.elder_id WHERE b.family_id = ?",
            (family_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Database error in user.get_bound_elders: {e}")
        return []
    finally:
        conn.close()
