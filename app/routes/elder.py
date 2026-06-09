from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app.models import status, reminder, user

elder_bp = Blueprint('elder', __name__, url_prefix='/elder')

@elder_bp.before_request
def require_elder_login():
    if 'user_id' not in session or session.get('role') != 'elder':
        flash('請先以長者身分登入', 'warning')
        return redirect(url_for('auth.login'))

@elder_bp.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    u = user.get_by_id(user_id)
    
    # 取得今日是否已打卡
    checkin_record = status.get_today_checkin(user_id)
    has_checked_in = checkin_record is not None

    # 取得今日提醒事項
    reminders = reminder.get_reminders_by_elder(user_id, active_only=True)

    return render_template('elder/dashboard.html', 
                           user=u, 
                           has_checked_in=has_checked_in, 
                           reminders=reminders)

@elder_bp.route('/checkin', methods=['POST'])
def checkin():
    user_id = session['user_id']
    record_id = status.create({
        'elder_id': user_id,
        'type': 'CHECKIN'
    })
    if record_id:
        flash('平安打卡成功！', 'success')
    else:
        flash('打卡失敗，請再試一次', 'danger')
    return redirect(url_for('elder.dashboard'))

@elder_bp.route('/sos', methods=['POST'])
def sos():
    user_id = session['user_id']
    record_id = status.create({
        'elder_id': user_id,
        'type': 'SOS'
    })
    if record_id:
        flash('緊急求助已送出！已通知聯絡人！', 'danger')
        # 未來擴充發送 Line Notify 等邏輯
    else:
        flash('求助發送失敗，請直接撥打電話！', 'danger')
    return redirect(url_for('elder.dashboard'))

@elder_bp.route('/api/reminders')
def get_reminders_api():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Unauthorized'}, 401
    
    # 取得今日提醒事項
    reminders = reminder.get_reminders_by_elder(user_id, active_only=True)
    
    # 轉換成 JSON
    reminders_list = []
    for r in reminders:
        reminders_list.append({
            'id': r['id'],
            'title': r['title'],
            'remind_time': r['remind_time']
        })
        
    return {'reminders': reminders_list}

