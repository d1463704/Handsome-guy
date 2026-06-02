"""認證路由 — 註冊 / 登入 / 登出"""
from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from app.models import user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        display_name = request.form.get('display_name')
        phone = request.form.get('phone')
        role = request.form.get('role')

        if not username or not password or not display_name or not role:
            flash('請填寫所有必填欄位', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = user.get_user_by_username(username)
        if existing_user:
            flash('此帳號已被使用，請選擇其他帳號', 'danger')
            return redirect(url_for('auth.register'))

        elder_code = None
        if role == 'elder':
            elder_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        password_hash = generate_password_hash(password)
        user_id = user.create({
            'role': role,
            'username': username,
            'password_hash': password_hash,
            'display_name': display_name,
            'phone': phone,
            'elder_code': elder_code
        })

        if user_id:
            flash('註冊成功！請登入', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('註冊失敗，請稍後再試', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        u = user.get_user_by_username(username)
        if u and check_password_hash(u['password_hash'], password):
            session['user_id'] = u['id']
            session['role'] = u['role']
            session['display_name'] = u['display_name']

            if u['role'] == 'elder':
                return redirect(url_for('elder.dashboard'))
            else:
                return redirect(url_for('family.dashboard'))
        else:
            flash('帳號或密碼錯誤', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))
