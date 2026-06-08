"""家屬路由 — 儀表板 / 綁定長者 / 管理提醒"""
from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app.models import user, status, reminder, reminder_log
from functools import wraps

family_bp = Blueprint('family', __name__)


def family_required(f):
    """裝飾器：確認使用者已登入且角色為家屬或護工"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') not in ('family', 'nurse'):
            flash('此頁面僅供家屬或護工使用', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@family_bp.before_request
def require_family_login():
    if 'user_id' not in session or session.get('role') not in ('family', 'nurse'):
        flash('請先以家屬身分登入', 'warning')
        return redirect(url_for('auth.login'))


@family_bp.route('/dashboard')
def dashboard():
    """家屬儀表板"""
    family_id = session['user_id']
    elders = user.get_bound_elders(family_id)

    elder_status = []
    for elder in elders:
        recent_records = status.get_records_by_elder(elder['id'], limit=5)
        checkin_today = status.get_today_checkin(elder['id'])
        has_checkin_today = checkin_today is not None
        today_mood = checkin_today['mood_score'] if checkin_today else None
        
        # 取得今日提醒事項與回覆狀態
        elder_reminders = reminder.get_reminders_by_elder(elder['id'], active_only=True)
        logs_with_comments = reminder_log.get_today_logs_with_comments_by_elder(elder['id'])
        reminders_with_status = []
        for r in elder_reminders:
            r_dict = dict(r)
            r_dict['log'] = logs_with_comments.get(r['id'])
            reminders_with_status.append(r_dict)

        elder_status.append({
            'elder': elder,
            'recent_records': recent_records,
            'has_checkin_today': has_checkin_today,
            'today_mood': today_mood,
            'reminders_with_status': reminders_with_status
        })

    return render_template('family/dashboard.html', elder_status=elder_status)

@family_bp.route('/api/logs/<int:log_id>/comment', methods=['POST'])
def api_reminder_comment(log_id):
    family_id = session.get('user_id')
    if not family_id or session.get('role') not in ('family', 'nurse'):
        return {"error": "Unauthorized"}, 401
        
    message = request.form.get('message', '').strip()
    if not message:
        return {"error": "Message is empty"}, 400
        
    comment_id = reminder_log.add_comment(log_id, family_id, message)
    if comment_id:
        flash('留言成功', 'success')
    else:
        flash('留言失敗', 'danger')
        
    return redirect(url_for('family.dashboard'))


@family_bp.route('/bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'POST':
        elder_code = request.form.get('elder_code', '').strip().upper()
        if not elder_code:
            flash('請輸入長者綁定碼', 'danger')
            return redirect(url_for('family.bind'))

        elder = user.get_user_by_elder_code(elder_code)
        if not elder:
            flash('找不到此綁定碼對應的長者，請確認後再試', 'danger')
            return redirect(url_for('family.bind'))

        success = user.bind_elder_to_family(session['user_id'], elder['id'])
        if success:
            flash(f'成功綁定長者 {elder["display_name"]}！', 'success')
            return redirect(url_for('family.dashboard'))
        else:
            flash('綁定失敗，或已綁定過此長者。', 'warning')

    return render_template('family/bind.html')


@family_bp.route('/reminders', methods=['GET', 'POST'])
def reminders():
    """提醒列表"""
    family_id = session['user_id']
    elders = user.get_bound_elders(family_id)

    if request.method == 'POST':
        elder_id = request.form.get('elder_id')
        title = request.form.get('title')
        remind_time = request.form.get('remind_time')

        if not elder_id or not title or not remind_time:
            flash('請填寫所有欄位', 'danger')
        else:
            reminder_id = reminder.create({
                'elder_id': elder_id,
                'created_by': family_id,
                'title': title,
                'remind_time': remind_time
            })
            if reminder_id:
                flash('提醒事項新增成功！', 'success')
            else:
                flash('新增失敗，請稍後再試', 'danger')
        return redirect(url_for('family.reminders'))

    all_reminders = []
    for elder in elders:
        elder_reminders = reminder.get_reminders_by_elder(elder['id'], active_only=False)
        all_reminders.append({
            'elder': elder,
            'reminders': elder_reminders
        })

    return render_template('family/reminders.html', elders=elders, all_reminders=all_reminders)


@family_bp.route('/reminders/<int:reminder_id>/toggle', methods=['POST'])
def toggle_reminder(reminder_id):
    r = reminder.get_by_id(reminder_id)
    if r:
        new_status = 0 if r['is_active'] == 1 else 1
        reminder.update_status(reminder_id, new_status)
        flash('提醒狀態已更新', 'success')
    return redirect(url_for('family.reminders'))


@family_bp.route('/reminders/<int:reminder_id>/delete', methods=['POST'])
def delete_reminder(reminder_id):
    success = reminder.delete(reminder_id)
    if success:
        flash('提醒事項已刪除', 'success')
    else:
        flash('刪除失敗', 'error')
    return redirect(url_for('family.reminders'))
