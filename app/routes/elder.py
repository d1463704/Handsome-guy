"""長者路由 — 平安打卡（含心情評分）/ 緊急求助 / 查看提醒"""
from flask import render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
from app.models import status, reminder, user, reminder_log

elder_bp = Blueprint('elder', __name__, url_prefix='/elder')


@elder_bp.before_request
def require_elder_login():
    if 'user_id' not in session or session.get('role') != 'elder':
        # 如果是 API 請求，回傳 JSON 格式的 401 錯誤，避免重定向 HTML
        if request.path.startswith('/elder/api/'):
            return jsonify({'error': 'Unauthorized'}), 401
        flash('請先以長者身分登入', 'warning')
        return redirect(url_for('auth.login'))


@elder_bp.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    u = user.get_by_id(user_id)

    # 今日是否已打卡
    checkin_record = status.get_today_checkin(user_id)
    has_checked_in = checkin_record is not None
    today_mood = checkin_record['mood_score'] if checkin_record else None

    # 今日提醒事項
    reminders = reminder.get_reminders_by_elder(user_id, active_only=True)
    logs_with_comments = reminder_log.get_today_logs_with_comments_by_elder(user_id)

    return render_template('elder/dashboard.html',
                           user=u,
                           has_checked_in=has_checked_in,
                           today_mood=today_mood,
                           reminders=reminders,
                           logs_with_comments=logs_with_comments)


@elder_bp.route('/checkin', methods=['POST'])
def checkin():
    user_id = session['user_id']

    # 確認今日尚未打卡
    if status.get_today_checkin(user_id):
        flash('您今天已經打過卡了！', 'info')
        return redirect(url_for('elder.dashboard'))

    mood_score = request.form.get('mood_score', type=int)
    if not mood_score or mood_score not in range(1, 6):
        flash('請選擇您今天的心情喔！', 'warning')
        return redirect(url_for('elder.dashboard'))

    record_id = status.create({
        'elder_id': user_id,
        'type': 'CHECKIN',
        'mood_score': mood_score
    })
    if record_id:
        mood_labels = {1: '😢 很不好', 2: '😟 不太好', 3: '😐 普通', 4: '😊 不錯', 5: '😄 很棒！'}
        flash(f'平安打卡成功！今日心情：{mood_labels.get(mood_score, "")}', 'success')
    else:
        flash('打卡失敗，請再試一次', 'danger')
    return redirect(url_for('elder.dashboard'))


@elder_bp.route('/sos', methods=['POST'])
def sos():
    user_id = session['user_id']
    record_id = status.create({
        'elder_id': user_id,
        'type': 'SOS',
        'mood_score': None
    })
    if record_id:
        flash('🚨 緊急求助已送出！已通知聯絡人！', 'danger')
    else:
        flash('求助發送失敗，請直接撥打電話！', 'danger')
    return redirect(url_for('elder.dashboard'))


@elder_bp.route('/api/reminders')
def api_reminders():
    """API：取得長者今日的未完成提醒事項與回覆狀態"""
    user_id = session.get('user_id')
    if not user_id or session.get('role') != 'elder':
        return jsonify({'error': 'Unauthorized'}), 401

    reminder_list = reminder.get_reminders_by_elder(user_id, active_only=True)
    logs_with_comments = reminder_log.get_today_logs_with_comments_by_elder(user_id)
    
    result = []
    for r in reminder_list:
        r_log = logs_with_comments.get(r['id'])
        result.append({
            'id': r['id'],
            'title': r['title'],
            'remind_time': r['remind_time'],
            'log': r_log  # 包含 status 與 comments
        })
    return jsonify({'reminders': result})

@elder_bp.route('/api/reminders/<int:reminder_id>/reply', methods=['POST'])
def api_reminder_reply(reminder_id):
    """API：長者回覆提醒狀態"""
    user_id = session.get('user_id')
    if not user_id or session.get('role') != 'elder':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    status = data.get('status')
    if status not in ('completed', 'difficult'):
        return jsonify({'error': 'Invalid status'}), 400

    log_id = reminder_log.log_reply(reminder_id, user_id, status)
    if log_id:
        return jsonify({'success': True, 'log_id': log_id})
    else:
        return jsonify({'error': 'Failed to log reply'}), 500

@elder_bp.route('/api/logs/<int:log_id>/comment', methods=['POST'])
def api_reminder_comment(log_id):
    """API：長者在提醒紀錄下留言"""
    user_id = session.get('user_id')
    if not user_id or session.get('role') != 'elder':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is empty'}), 400

    comment_id = reminder_log.add_comment(log_id, user_id, message)
    if comment_id:
        return jsonify({'success': True, 'comment_id': comment_id})
    else:
        return jsonify({'error': 'Failed to add comment'}), 500
