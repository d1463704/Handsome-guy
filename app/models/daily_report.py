"""
每日回報模型（DailyReport Model）
處理長者每日生活回報的 CRUD 操作。
"""
from app import get_db
from datetime import date


class DailyReport:
    """每日回報模型"""

    @staticmethod
    def create(user_id, status='safe', note=None):
        """
        建立每日回報

        Args:
            user_id (int): 長者的 user_id
            status (str): 回報狀態 ('safe' / 'need_help')
            note (str, optional): 備註

        Returns:
            int: 新建回報的 id，失敗回傳 None
        """
        try:
            db = get_db()
            cursor = db.execute(
                '''INSERT INTO daily_reports (user_id, status, note)
                   VALUES (?, ?, ?)''',
                (user_id, status, note)
            )
            db.commit()
            report_id = cursor.lastrowid
            db.close()
            return report_id
        except Exception as e:
            print(f"[DailyReport.create] 錯誤：{e}")
            return None

    @staticmethod
    def get_all():
        """取得所有回報紀錄"""
        try:
            db = get_db()
            reports = db.execute(
                '''SELECT dr.*, u.display_name
                   FROM daily_reports dr
                   JOIN users u ON dr.user_id = u.id
                   ORDER BY dr.reported_at DESC'''
            ).fetchall()
            db.close()
            return reports
        except Exception as e:
            print(f"[DailyReport.get_all] 錯誤：{e}")
            return []

    @staticmethod
    def get_by_id(report_id):
        """依 ID 取得單筆回報"""
        try:
            db = get_db()
            report = db.execute(
                'SELECT * FROM daily_reports WHERE id = ?', (report_id,)
            ).fetchone()
            db.close()
            return report
        except Exception as e:
            print(f"[DailyReport.get_by_id] 錯誤：{e}")
            return None

    @staticmethod
    def get_today(user_id):
        """
        取得長者今日的回報

        Args:
            user_id (int): 長者的 user_id

        Returns:
            sqlite3.Row or None: 今日回報資料
        """
        try:
            db = get_db()
            today = date.today().isoformat()
            report = db.execute(
                '''SELECT * FROM daily_reports
                   WHERE user_id = ? AND DATE(reported_at) = ?
                   ORDER BY reported_at DESC LIMIT 1''',
                (user_id, today)
            ).fetchone()
            db.close()
            return report
        except Exception as e:
            print(f"[DailyReport.get_today] 錯誤：{e}")
            return None

    @staticmethod
    def get_by_elder(elder_id, limit=30):
        """
        取得指定長者的回報歷史

        Args:
            elder_id (int): 長者的 user_id
            limit (int): 最多回傳幾筆

        Returns:
            list: 回報紀錄列表
        """
        try:
            db = get_db()
            reports = db.execute(
                '''SELECT * FROM daily_reports
                   WHERE user_id = ?
                   ORDER BY reported_at DESC
                   LIMIT ?''',
                (elder_id, limit)
            ).fetchall()
            db.close()
            return reports
        except Exception as e:
            print(f"[DailyReport.get_by_elder] 錯誤：{e}")
            return []

    @staticmethod
    def get_by_family(family_id, limit=50):
        """
        取得家屬所綁定長者的回報紀錄

        Args:
            family_id (int): 家屬的 user_id
            limit (int): 最多回傳幾筆

        Returns:
            list: 回報紀錄列表
        """
        try:
            db = get_db()
            reports = db.execute(
                '''SELECT dr.*, u.display_name
                   FROM daily_reports dr
                   JOIN users u ON dr.user_id = u.id
                   JOIN user_bindings efl ON dr.user_id = efl.elder_id
                   WHERE efl.family_id = ?
                   ORDER BY dr.reported_at DESC
                   LIMIT ?''',
                (family_id, limit)
            ).fetchall()
            db.close()
            return reports
        except Exception as e:
            print(f"[DailyReport.get_by_family] 錯誤：{e}")
            return []

    @staticmethod
    def update(report_id, data):
        """更新回報紀錄"""
        try:
            db = get_db()
            fields = []
            values = []
            for key, value in data.items():
                if key in ('status', 'note'):
                    fields.append(f'{key} = ?')
                    values.append(value)
            if not fields:
                return False
            values.append(report_id)
            db.execute(
                f'UPDATE daily_reports SET {", ".join(fields)} WHERE id = ?',
                values
            )
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[DailyReport.update] 錯誤：{e}")
            return False

    @staticmethod
    def delete(report_id):
        """刪除回報紀錄"""
        try:
            db = get_db()
            db.execute('DELETE FROM daily_reports WHERE id = ?', (report_id,))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[DailyReport.delete] 錯誤：{e}")
            return False
