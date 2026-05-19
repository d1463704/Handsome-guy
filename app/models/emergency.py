"""
緊急通報模型（Emergency Model）
"""
from app import get_db


class Emergency:
    @staticmethod
    def create(user_id, message=None):
        try:
            db = get_db()
            cursor = db.execute(
                'INSERT INTO emergencies (user_id, message) VALUES (?, ?)',
                (user_id, message))
            db.commit()
            eid = cursor.lastrowid
            db.close()
            return eid
        except Exception as e:
            print(f"[Emergency.create] {e}")
            return None

    @staticmethod
    def get_all():
        try:
            db = get_db()
            rows = db.execute(
                '''SELECT e.*, u.display_name FROM emergencies e
                   JOIN users u ON e.user_id = u.id
                   ORDER BY e.created_at DESC''').fetchall()
            db.close()
            return rows
        except Exception as e:
            print(f"[Emergency.get_all] {e}")
            return []

    @staticmethod
    def get_by_id(eid):
        try:
            db = get_db()
            row = db.execute('SELECT * FROM emergencies WHERE id = ?', (eid,)).fetchone()
            db.close()
            return row
        except Exception as e:
            print(f"[Emergency.get_by_id] {e}")
            return None

    @staticmethod
    def get_by_elder(elder_id, limit=20):
        try:
            db = get_db()
            rows = db.execute(
                'SELECT * FROM emergencies WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                (elder_id, limit)).fetchall()
            db.close()
            return rows
        except Exception as e:
            print(f"[Emergency.get_by_elder] {e}")
            return []

    @staticmethod
    def get_by_family(family_id, limit=50):
        try:
            db = get_db()
            rows = db.execute(
                '''SELECT e.*, u.display_name FROM emergencies e
                   JOIN users u ON e.user_id = u.id
                   JOIN elder_family_link efl ON e.user_id = efl.elder_id
                   WHERE efl.family_id = ? ORDER BY e.created_at DESC LIMIT ?''',
                (family_id, limit)).fetchall()
            db.close()
            return rows
        except Exception as e:
            print(f"[Emergency.get_by_family] {e}")
            return []

    @staticmethod
    def get_pending_by_family(family_id):
        try:
            db = get_db()
            rows = db.execute(
                '''SELECT e.*, u.display_name FROM emergencies e
                   JOIN users u ON e.user_id = u.id
                   JOIN elder_family_link efl ON e.user_id = efl.elder_id
                   WHERE efl.family_id = ? AND e.status = 'pending'
                   ORDER BY e.created_at DESC''',
                (family_id,)).fetchall()
            db.close()
            return rows
        except Exception as e:
            print(f"[Emergency.get_pending_by_family] {e}")
            return []

    @staticmethod
    def resolve(eid, resolved_by):
        try:
            db = get_db()
            db.execute(
                '''UPDATE emergencies SET status='resolved', resolved_by=?,
                   resolved_at=datetime('now','localtime') WHERE id=?''',
                (resolved_by, eid))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[Emergency.resolve] {e}")
            return False

    @staticmethod
    def delete(eid):
        try:
            db = get_db()
            db.execute('DELETE FROM emergencies WHERE id = ?', (eid,))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"[Emergency.delete] {e}")
            return False
