"""
獨居老人生活管家 - Flask 應用程式初始化
"""
import os
import sqlite3
from flask import Flask


def create_app():
    """Flask App Factory"""
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='templates',
                static_folder='static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')

    os.makedirs(app.instance_path, exist_ok=True)

    init_db(app)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.elder import elder_bp
    from app.routes.family import family_bp

    # Blueprints already define url_prefix internally
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(elder_bp)
    app.register_blueprint(family_bp)

    return app


def get_db(app=None):
    """取得資料庫連線"""
    if app is None:
        from flask import current_app
        app = current_app

    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(app):
    """初始化資料庫（執行 schema.sql 建表）"""
    db_path = app.config['DATABASE']
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')

    if os.path.exists(schema_path):
        conn = sqlite3.connect(db_path)
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.close()
