"""
獨居老人生活管家 — 應用程式入口點
"""
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
