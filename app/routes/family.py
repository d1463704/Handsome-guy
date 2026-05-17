from flask import render_template, request, redirect, url_for, flash, session
from . import family_bp

@family_bp.route('/dashboard')
def dashboard():
    """
    家屬與護工的主控台首頁。
    需要檢查是否已登入且身分為 family。
    取得該帳號綁定的所有長者清單與今日最新狀態。
    """
    pass

@family_bp.route('/bind', methods=['GET', 'POST'])
def bind():
    """
    長者綁定功能。
    GET: 顯示輸入綁定碼的畫面。
    POST: 接收 elder_code，驗證成功後將雙方 ID 寫入 user_bindings 表。
    """
    if request.method == 'POST':
        pass
    return render_template('family/bind.html')

@family_bp.route('/reminders', methods=['GET', 'POST'])
def reminders():
    """
    提醒事項管理。
    GET: 列出家屬為長者設定的所有提醒事項。
    POST: 新增提醒事項。
    """
    if request.method == 'POST':
        pass
    return render_template('family/reminders.html')

@family_bp.route('/reminders/<int:reminder_id>/toggle', methods=['POST'])
def toggle_reminder(reminder_id):
    """
    啟用或停用某個提醒事項。
    更新 reminders 表的 is_active 欄位。
    """
    pass

@family_bp.route('/reminders/<int:reminder_id>/delete', methods=['POST'])
def delete_reminder(reminder_id):
    """
    刪除某個提醒事項。
    從 reminders 表移除。
    """
    pass
