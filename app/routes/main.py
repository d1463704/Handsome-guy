"""
主頁路由 — 首頁與導向
"""
from flask import Blueprint, redirect, url_for, session, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首頁：已登入則依角色重導向，否則導向登入頁"""
    if 'user_id' in session:
        role = session.get('role', '')
        if role == 'elder':
            return redirect(url_for('elder.dashboard'))
        elif role in ('family', 'nurse'):
            return redirect(url_for('family.dashboard'))
    return redirect(url_for('auth.login'))
