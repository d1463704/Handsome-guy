# Routes 模組初始化
from .auth import auth_bp
from .elder import elder_bp
from .family import family_bp

def init_app(app):
    """
    提供給主程式 (app.py) 呼叫，用來註冊所有的 Blueprint
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(elder_bp)
    app.register_blueprint(family_bp)
