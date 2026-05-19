"""認證路由 — 註冊/登入/登出"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登入"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請填寫帳號與密碼', 'error')
            return render_template('auth/login.html')

        user = User.get_by_username(username)
        if user and User.verify_password(user, password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['display_name'] = user['display_name']
            flash(f'歡迎回來，{user["display_name"]}！', 'success')

            if user['role'] == 'elder':
                return redirect(url_for('elder.dashboard'))
            else:
                return redirect(url_for('family.dashboard'))
        else:
            flash('帳號或密碼錯誤', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """註冊"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()
        role = request.form.get('role', '')
        phone = request.form.get('phone', '').strip() or None

        # 驗證
        if not all([username, password, display_name, role]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('兩次輸入的密碼不一致', 'error')
            return render_template('auth/register.html')

        if role not in ('elder', 'family', 'nurse'):
            flash('請選擇正確的角色', 'error')
            return render_template('auth/register.html')

        if len(password) < 4:
            flash('密碼至少需要 4 個字元', 'error')
            return render_template('auth/register.html')

        # 建立帳號
        user_id = User.create(username, password, display_name, role, phone)
        if user_id:
            flash('註冊成功！請登入', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('帳號已存在，請使用其他帳號', 'error')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('main.index'))
