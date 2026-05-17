from .db import get_db_connection

def create_user(role, username, password_hash, display_name, phone=None, elder_code=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (role, username, password_hash, display_name, phone, elder_code) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (role, username, password_hash, display_name, phone, elder_code)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_elder_code(elder_code):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE elder_code = ? AND role = 'elder'", (elder_code,)).fetchone()
    conn.close()
    return user

def bind_elder_to_family(family_id, elder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_bindings (family_id, elder_id) VALUES (?, ?)",
            (family_id, elder_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 已經綁定過了
        return False
    finally:
        conn.close()

def get_bound_elders(family_id):
    """取得家屬綁定的所有長者"""
    conn = get_db_connection()
    elders = conn.execute(
        "SELECT u.* FROM users u "
        "JOIN user_bindings b ON u.id = b.elder_id "
        "WHERE b.family_id = ?",
        (family_id,)
    ).fetchall()
    conn.close()
    return elders

def get_bound_families(elder_id):
    """取得長者被綁定的所有家屬"""
    conn = get_db_connection()
    families = conn.execute(
        "SELECT u.* FROM users u "
        "JOIN user_bindings b ON u.id = b.family_id "
        "WHERE b.elder_id = ?",
        (elder_id,)
    ).fetchall()
    conn.close()
    return families
