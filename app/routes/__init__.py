from flask import Blueprint

# 定義各個模組的 Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
elder_bp = Blueprint('elder', __name__, url_prefix='/elder')
family_bp = Blueprint('family', __name__, url_prefix='/family')

# 在下方匯入各個模組以註冊路由
from . import auth, elder, family

def init_app(app):
    """
    提供給主程式 (app.py) 呼叫，用來註冊所有的 Blueprint
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(elder_bp)
    app.register_blueprint(family_bp)
