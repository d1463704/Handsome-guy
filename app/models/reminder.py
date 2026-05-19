"""
事項提醒模型（Reminder Model）
處理提醒事項的 CRUD 操作。
"""
from app import get_db
from datetime import datetime, date


class Reminder:
    """事項提醒模型"""

    @staticmethod
    def create(elder_id, created_by, title, remind_time, repeat_type='daily',
               description=None, due_date=None):
        """
        建立新的提醒事項

        Args:
            elder_id (int): 長者的 user_id
            created_by (int): 建立者的 user_id
            title (str): 提醒標題
            remind_time (str): 提醒時間 (HH:MM)
            repeat_type (str): 重複類型 ('daily' / 'weekly' / 'once')
            description (str, optional): 提醒內容
            due_date (str, optional): 到期日期

        Returns:
            int: 新建提醒的 id，失敗回傳 None
        """
        try:
            db = get_db()
            cursor = db.execute(
                '''INSERT INTO reminders
                   (elder_id, created_by, title, description, remind_time, repeat_type, due_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (elder_id, created_by, title, description, remind_time, repeat_type, due_date)
            )
            db.commit()
            reminder_id = cursor.lastrowid
            db.close()
            return reminder_id
        except Exception as e:
            print(f"[Reminder.create] 錯誤：{e}")
            return None

    @staticmethod
    def get_all():
        """取得所有提醒事項"""
        try:
            db = get_db()
            reminders = db.execute(
                '''SELECT r.*, u.display_name as elder_name
                   FROM reminders r
                   JOIN users u ON r.elder_id = u.id
                   ORDER BY r.remind_time'''
            ).fetchall()
            db.close()
            return reminders
        except Exception as e:
            print(f"[Reminder.get_all] 錯誤：{e}")
            return []

    @staticmethod
    def get_by_id(reminder_id):
        """依 ID 取得單筆提醒"""
        try:
            db = get_db()
            reminder = db.execute(
                'SELECT * FROM reminders WHERE id = ?', (reminder_id,)
            ).fetchone()
            db.close()
            return reminder
        except Exception as e:
            print(f"[Reminder.get_by_id] 錯誤：{e}")
            return None

    @staticmethod
    def get_by_elder(elder_id):
        """
        取得指定長者的所有提醒（今日有效的）

        Args:
            elder_id (int): 長者的 user_id

        Returns:
            list: 提醒列表
        """
        try:
            db = get_db()
            today = date.today().isoformat()
            reminders = db.execute(
                '''SELECT * FROM reminders
                   WHERE elder_id = ?
                   AND (repeat_type != 'once' OR due_date >= ? OR due_date IS NULL)
                   ORDER BY remind_time''',
                (elder_id, today)
            ).fetchall()
            db.close()
            return reminders
        except Exception as e:
            print(f"[Reminder.get_by_elder] 錯誤：{e}")
            return []

    @staticmethod
    def get_by_family(family_id):
        """
        取得家屬所綁定長者的所有提醒

        Args:
            family_id (int): 家屬的 user_id

        Returns:
            list: 提醒列表
        """
        try:
            db = get_db()
            reminders = db.execute(
                '''SELECT r.*, u.display_name as elder_name
                   FROM reminders r
                   JOIN users u ON r.elder_id = u.id
                   JOIN elder_family_link efl ON r.elder_id = efl.elder_id
                   WHERE efl.family_id = ?
                   ORDER BY r.remind_time''',
                (family_id,)
            ).fetchall()
            db.close()
            return reminders
        except Exception as e:
            print(f"[Reminder.get_by_family] 錯誤：{e}")
            return []

    @staticmethod
    def get_pending_count(elder_id):
        """取得長者待完成的提醒數量"""
        try:
            db = get_db()
            result = db.execute(
                "SELECT COUNT(*) as count FROM reminders WHERE elder_id = ? AND status = 'pending'",
                (elder_id,)
            ).fetchone()
            db.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"[Reminder.get_pending_count] 錯誤：{e}")
            return 0

    @staticmethod
    def update(reminder_id, data):
        """
        更新提醒事項

        Args:
            reminder_id (int): 提醒 ID
            data (dict): 要更新的欄位

        Returns:
            bool: 是否更新成功
        """
        try:
            db = get_db()
            fields = []
            values = []
            allowed_fields = ('title', 'description', 'remind_time', 'repeat_type',
                              'status', 'due_date')
            for key, value in data.items():
                if key in allowed_fields:
                    fields.append(f'{key} = ?')
                    values.append(value)

            if not fields:
                return False

            # 更新 updated_at
            fields.append("updated_at = datetime('now', 'localtime')")

            values.append(reminder_id)
            db.execute(
                f'UPDATE reminders SET {", ".join(fields)} WHERE id = ?',
                values
            )
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[Reminder.update] 錯誤：{e}")
            return False

    @staticmethod
    def complete(reminder_id):
        """標記提醒為已完成"""
        return Reminder.update(reminder_id, {'status': 'completed'})

    @staticmethod
    def reset_daily():
        """重置每日提醒的狀態（每天呼叫一次）"""
        try:
            db = get_db()
            db.execute(
                "UPDATE reminders SET status = 'pending' WHERE repeat_type = 'daily'"
            )
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[Reminder.reset_daily] 錯誤：{e}")
            return False

    @staticmethod
    def delete(reminder_id):
        """刪除提醒事項"""
        try:
            db = get_db()
            db.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[Reminder.delete] 錯誤：{e}")
            return False
