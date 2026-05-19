"""長者路由 — 每日回報/緊急求助/查看提醒"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models.daily_report import DailyReport
from app.models.emergency import Emergency
from app.models.reminder import Reminder

elder_bp = Blueprint('elder', __name__)


def elder_required(f):
    """裝飾器：確認使用者已登入且角色為長者"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'elder':
            flash('此頁面僅供長者使用', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@elder_bp.route('/dashboard')
@elder_required
def dashboard():
    """長者主頁 — 大按鈕介面"""
    user_id = session['user_id']
    reported_today = DailyReport.get_today(user_id) is not None
    pending_count = Reminder.get_pending_count(user_id)
    return render_template('elder/dashboard.html',
                           reported_today=reported_today,
                           pending_count=pending_count)


@elder_bp.route('/daily-report', methods=['POST'])
@elder_required
def daily_report():
    """每日回報"""
    user_id = session['user_id']
    existing = DailyReport.get_today(user_id)
    if existing:
        flash('您今天已經回報過了！', 'info')
    else:
        status = request.form.get('status', 'safe')
        note = request.form.get('note', '').strip() or None
        result = DailyReport.create(user_id, status, note)
        if result:
            flash('回報成功！感謝您的回報 😊', 'success')
        else:
            flash('回報失敗，請稍後再試', 'error')
    return redirect(url_for('elder.dashboard'))


@elder_bp.route('/emergency', methods=['POST'])
@elder_required
def emergency():
    """緊急求助"""
    user_id = session['user_id']
    message = request.form.get('message', '').strip() or '緊急求助'
    result = Emergency.create(user_id, message)
    if result:
        flash('🚨 已發送緊急通報，家屬將會收到通知！', 'warning')
    else:
        flash('通報失敗，請稍後再試', 'error')
    return redirect(url_for('elder.dashboard'))


@elder_bp.route('/reminders')
@elder_required
def reminders():
    """查看提醒列表"""
    user_id = session['user_id']
    reminder_list = Reminder.get_by_elder(user_id)
    return render_template('elder/reminders.html', reminders=reminder_list)


@elder_bp.route('/reminders/<int:reminder_id>/complete', methods=['POST'])
@elder_required
def complete_reminder(reminder_id):
    """標記提醒為已完成"""
    result = Reminder.complete(reminder_id)
    if result:
        flash('已完成！做得好 👍', 'success')
    else:
        flash('操作失敗', 'error')
    return redirect(url_for('elder.reminders'))
