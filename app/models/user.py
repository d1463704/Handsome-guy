"""
使用者模型（User Model）
處理使用者的 CRUD 操作，包含註冊、登入驗證。
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db


class User:
    """使用者模型"""

    @staticmethod
    def create(username, password, display_name, role, phone=None):
        """
        建立新使用者

        Args:
            username (str): 帳號（唯一）
            password (str): 明文密碼（會自動雜湊）
            display_name (str): 顯示名稱
            role (str): 角色 ('elder' / 'family' / 'nurse')
            phone (str, optional): 聯絡電話

        Returns:
            int: 新建使用者的 id，失敗回傳 None
        """
        try:
            db = get_db()
            password_hash = generate_password_hash(password)
            cursor = db.execute(
                '''INSERT INTO users (username, password_hash, display_name, role, phone)
                   VALUES (?, ?, ?, ?, ?)''',
                (username, password_hash, display_name, role, phone)
            )
            db.commit()
            user_id = cursor.lastrowid
            db.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"[User.create] 錯誤：{e}")
            return None

    @staticmethod
    def get_all():
        """
        取得所有使用者

        Returns:
            list: 使用者列表（sqlite3.Row 物件）
        """
        try:
            db = get_db()
            users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
            db.close()
            return users
        except Exception as e:
            print(f"[User.get_all] 錯誤：{e}")
            return []

    @staticmethod
    def get_by_id(user_id):
        """
        依 ID 取得使用者

        Args:
            user_id (int): 使用者 ID

        Returns:
            sqlite3.Row or None: 使用者資料
        """
        try:
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            db.close()
            return user
        except Exception as e:
            print(f"[User.get_by_id] 錯誤：{e}")
            return None

    @staticmethod
    def get_by_username(username):
        """
        依帳號取得使用者

        Args:
            username (str): 帳號

        Returns:
            sqlite3.Row or None: 使用者資料
        """
        try:
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            db.close()
            return user
        except Exception as e:
            print(f"[User.get_by_username] 錯誤：{e}")
            return None

    @staticmethod
    def verify_password(user, password):
        """
        驗證密碼

        Args:
            user (sqlite3.Row): 使用者資料
            password (str): 明文密碼

        Returns:
            bool: 密碼是否正確
        """
        if user is None:
            return False
        return check_password_hash(user['password_hash'], password)

    @staticmethod
    def update(user_id, data):
        """
        更新使用者資料

        Args:
            user_id (int): 使用者 ID
            data (dict): 要更新的欄位

        Returns:
            bool: 是否更新成功
        """
        try:
            db = get_db()
            fields = []
            values = []
            for key, value in data.items():
                if key in ('display_name', 'phone', 'role'):
                    fields.append(f'{key} = ?')
                    values.append(value)

            if not fields:
                return False

            values.append(user_id)
            db.execute(
                f'UPDATE users SET {", ".join(fields)} WHERE id = ?',
                values
            )
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[User.update] 錯誤：{e}")
            return False

    @staticmethod
    def delete(user_id):
        """
        刪除使用者

        Args:
            user_id (int): 使用者 ID

        Returns:
            bool: 是否刪除成功
        """
        try:
            db = get_db()
            db.execute('DELETE FROM users WHERE id = ?', (user_id,))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[User.delete] 錯誤：{e}")
            return False

    @staticmethod
    def get_elders_by_role():
        """取得所有角色為長者的使用者"""
        try:
            db = get_db()
            elders = db.execute(
                "SELECT * FROM users WHERE role = 'elder' ORDER BY display_name"
            ).fetchall()
            db.close()
            return elders
        except Exception as e:
            print(f"[User.get_elders_by_role] 錯誤：{e}")
            return []
