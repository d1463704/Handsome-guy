from flask import render_template, request, redirect, url_for, flash, session
from . import elder_bp

@elder_bp.route('/dashboard')
def dashboard():
    """
    長者的主控台首頁。
    需要檢查是否已登入且身分為 elder。
    載入當天提醒事項與當天打卡狀態，並顯示打卡/SOS大按鈕。
    """
    pass

@elder_bp.route('/checkin', methods=['POST'])
def checkin():
    """
    處理長者的「平安打卡」操作。
    寫入 status_records 表中，type 為 CHECKIN。
    處理完後重新導回 dashboard。
    """
    pass

@elder_bp.route('/sos', methods=['POST'])
def sos():
    """
    處理長者的「緊急求助」操作。
    寫入 status_records 表中，type 為 SOS。
    未來可擴充自動寄信或呼叫 LINE Notify 的邏輯。
    處理完後重新導回 dashboard，並顯示求救已送出。
    """
    pass
