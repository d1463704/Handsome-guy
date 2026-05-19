"""
獨居老人生活管家 — 應用程式入口點
"""
from app import create_app
import os
from flask import Flask
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='app/templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # 註冊 Blueprints
    from app.routes import init_app
    init_app(app)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
