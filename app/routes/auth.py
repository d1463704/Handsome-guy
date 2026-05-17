from flask import render_template, request, redirect, url_for, flash, session
from . import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    顯示註冊表單，並處理註冊邏輯。
    若是長者角色，註冊後將自動配發 elder_code。
    """
    if request.method == 'POST':
        pass
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    顯示登入表單，並處理登入邏輯。
    登入成功後，將 session['user_id'] 與 session['role'] 存起來，
    並依據 role 導向至 elder 或 family 的 dashboard。
    """
    if request.method == 'POST':
        pass
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    清除 session 並重導向至登入頁面。
    """
    pass
