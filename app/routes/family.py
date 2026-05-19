"""家屬/護工路由 — 儀表板/管理提醒/查看紀錄"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models.reminder import Reminder
from app.models.daily_report import DailyReport
from app.models.emergency import Emergency
from app.models.user import User
from app import get_db

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


def get_linked_elders(family_id):
    """取得家屬綁定的長者列表"""
    try:
        db = get_db()
        elders = db.execute(
            '''SELECT u.* FROM users u
               JOIN elder_family_link efl ON u.id = efl.elder_id
               WHERE efl.family_id = ?''',
            (family_id,)).fetchall()
        db.close()
        return elders
    except Exception:
        return []


@family_bp.route('/dashboard')
@family_required
def dashboard():
    """家屬儀表板"""
    family_id = session['user_id']
    elders = get_linked_elders(family_id)

    elders_status = []
    for elder in elders:
        today_report = DailyReport.get_today(elder['id'])
        pending = Reminder.get_pending_count(elder['id'])
        emergencies = Emergency.get_pending_by_family(family_id)
        elder_emergencies = [e for e in emergencies if e['user_id'] == elder['id']]

        elders_status.append({
            'elder': elder,
            'reported_today': today_report is not None,
            'report_status': today_report['status'] if today_report else None,
            'pending_reminders': pending,
            'emergency_count': len(elder_emergencies)
        })

    return render_template('family/dashboard.html', elders_status=elders_status)


@family_bp.route('/reminders')
@family_required
def reminders():
    """提醒列表"""
    family_id = session['user_id']
    reminder_list = Reminder.get_by_family(family_id)
    return render_template('family/reminders.html', reminders=reminder_list)


@family_bp.route('/reminders/new')
@family_required
def new_reminder():
    """新增提醒頁"""
    family_id = session['user_id']
    elders = get_linked_elders(family_id)
    return render_template('family/reminder_form.html', reminder=None, elders=elders)


@family_bp.route('/reminders', methods=['POST'])
@family_required
def create_reminder():
    """建立提醒"""
    elder_id = request.form.get('elder_id', type=int)
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip() or None
    remind_time = request.form.get('remind_time', '').strip()
    repeat_type = request.form.get('repeat_type', 'daily')
    due_date = request.form.get('due_date', '').strip() or None

    if not all([elder_id, title, remind_time]):
        flash('請填寫必填欄位（長者、標題、時間）', 'error')
        return redirect(url_for('family.new_reminder'))

    result = Reminder.create(
        elder_id=elder_id,
        created_by=session['user_id'],
        title=title,
        remind_time=remind_time,
        repeat_type=repeat_type,
        description=description,
        due_date=due_date)

    if result:
        flash('提醒已新增', 'success')
    else:
        flash('新增失敗', 'error')
    return redirect(url_for('family.reminders'))


@family_bp.route('/reminders/<int:rid>/edit')
@family_required
def edit_reminder(rid):
    """編輯提醒頁"""
    reminder = Reminder.get_by_id(rid)
    if not reminder:
        flash('找不到此提醒', 'error')
        return redirect(url_for('family.reminders'))
    family_id = session['user_id']
    elders = get_linked_elders(family_id)
    return render_template('family/reminder_form.html', reminder=reminder, elders=elders)


@family_bp.route('/reminders/<int:rid>/update', methods=['POST'])
@family_required
def update_reminder(rid):
    """更新提醒"""
    data = {
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip() or None,
        'remind_time': request.form.get('remind_time', '').strip(),
        'repeat_type': request.form.get('repeat_type', 'daily'),
        'due_date': request.form.get('due_date', '').strip() or None,
    }
    if not data['title'] or not data['remind_time']:
        flash('標題與時間為必填', 'error')
        return redirect(url_for('family.edit_reminder', rid=rid))

    Reminder.update(rid, data)
    flash('提醒已更新', 'success')
    return redirect(url_for('family.reminders'))


@family_bp.route('/reminders/<int:rid>/delete', methods=['POST'])
@family_required
def delete_reminder(rid):
    """刪除提醒"""
    Reminder.delete(rid)
    flash('提醒已刪除', 'success')
    return redirect(url_for('family.reminders'))


@family_bp.route('/reports')
@family_required
def reports():
    """回報紀錄"""
    family_id = session['user_id']
    report_list = DailyReport.get_by_family(family_id)
    return render_template('family/reports.html', reports=report_list)


@family_bp.route('/emergencies')
@family_required
def emergencies():
    """緊急通報紀錄"""
    family_id = session['user_id']
    emergency_list = Emergency.get_by_family(family_id)
    return render_template('family/emergencies.html', emergencies=emergency_list)


@family_bp.route('/emergencies/<int:eid>/resolve', methods=['POST'])
@family_required
def resolve_emergency(eid):
    """處理通報"""
    Emergency.resolve(eid, session['user_id'])
    flash('已標記為已處理', 'success')
    return redirect(url_for('family.emergencies'))


@family_bp.route('/link', methods=['GET', 'POST'])
@family_required
def link_elder():
    """綁定長者"""
    if request.method == 'POST':
        elder_username = request.form.get('elder_username', '').strip()
        if not elder_username:
            flash('請輸入長者的帳號', 'error')
            return render_template('family/link.html')

        elder = User.get_by_username(elder_username)
        if not elder:
            flash('找不到此帳號', 'error')
            return render_template('family/link.html')
        if elder['role'] != 'elder':
            flash('該帳號不是長者帳號', 'error')
            return render_template('family/link.html')

        try:
            db = get_db()
            db.execute(
                'INSERT INTO elder_family_link (elder_id, family_id) VALUES (?, ?)',
                (elder['id'], session['user_id']))
            db.commit()
            db.close()
            flash(f'已成功綁定長者「{elder["display_name"]}」', 'success')
            return redirect(url_for('family.dashboard'))
        except Exception:
            flash('綁定失敗，可能已經綁定過了', 'error')

    return render_template('family/link.html')
from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app.models import user, status, reminder

family_bp = Blueprint('family', __name__, url_prefix='/family')

@family_bp.before_request
def require_family_login():
    if 'user_id' not in session or session.get('role') != 'family':
        flash('請先以家屬身分登入', 'warning')
        return redirect(url_for('auth.login'))

@family_bp.route('/dashboard')
def dashboard():
    family_id = session['user_id']
    elders = user.get_bound_elders(family_id)
    
    elder_status = []
    for elder in elders:
        recent_records = status.get_records_by_elder(elder['id'], limit=5)
        has_checkin_today = status.get_today_checkin(elder['id']) is not None
        elder_status.append({
            'elder': elder,
            'recent_records': recent_records,
            'has_checkin_today': has_checkin_today
        })
        
    return render_template('family/dashboard.html', elder_status=elder_status)

@family_bp.route('/bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'POST':
        elder_code = request.form.get('elder_code')
        if not elder_code:
            flash('請輸入長者綁定碼', 'danger')
            return redirect(url_for('family.bind'))
            
        elder = user.get_user_by_elder_code(elder_code)
        if not elder:
            flash('找不到此綁定碼對應的長者', 'danger')
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
                flash('新增失敗', 'danger')
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
        flash('刪除失敗', 'danger')
    return redirect(url_for('family.reminders'))
