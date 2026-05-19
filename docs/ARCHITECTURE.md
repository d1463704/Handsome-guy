# 獨居老人生活管家 — 系統架構設計

> **對應文件**：[PRD](./PRD.md)  
> **版本**：v1.0  
> **最後更新**：2026-05-19

---

## 1. 技術架構說明

### 1.1 技術選型

| 層面 | 技術 | 說明 |
| :--- | :--- | :--- |
| 後端框架 | Python + Flask | 輕量級 Web 框架，適合快速開發，課堂指定 |
| 模板引擎 | Jinja2 | Flask 內建，負責 HTML 頁面渲染 |
| 資料庫 | SQLite | 輕量單檔資料庫，無需額外安裝，適合小型專案 |
| 前端 | HTML / CSS / JavaScript | 純前端技術，無框架依賴 |
| CSS 框架 | Bootstrap 5 (CDN) | 提供響應式佈局與基礎元件，加速前端開發 |
| 密碼雜湊 | Werkzeug (generate_password_hash) | Flask 內建的安全密碼處理工具 |

### 1.2 MVC 架構模式

本專案採用 **MVC（Model-View-Controller）** 架構：

```
┌──────────────────────────────────────────────────────┐
│                     使用者瀏覽器                       │
│            (HTML / CSS / JavaScript)                  │
└────────────┬─────────────────────┬────────────────────┘
             │ HTTP Request        │ HTTP Response (HTML)
             ▼                     │
┌──────────────────────────────────┴────────────────────┐
│              Controller（Flask Routes）                │
│              app/routes/*.py                          │
│  - 接收使用者請求                                      │
│  - 呼叫 Model 處理資料                                 │
│  - 選擇 View（模板）回傳                               │
└────────────┬─────────────────────┬────────────────────┘
             │                     │
     ┌───────▼───────┐     ┌──────▼───────┐
     │     Model     │     │     View     │
     │ app/models/   │     │ app/templates│
     │  *.py         │     │  *.html      │
     │               │     │              │
     │ - 資料庫操作   │     │ - Jinja2 模板│
     │ - CRUD 方法   │     │ - 頁面呈現   │
     │ - 商業邏輯    │     │ - 表單介面   │
     └───────┬───────┘     └──────────────┘
             │
             ▼
     ┌───────────────┐
     │    SQLite      │
     │ instance/      │
     │ database.db    │
     └───────────────┘
```

- **Model**（`app/models/`）：負責資料庫操作與商業邏輯，每個資料表對應一個 Python 檔案。
- **View**（`app/templates/`）：Jinja2 HTML 模板，負責頁面呈現與使用者互動介面。
- **Controller**（`app/routes/`）：Flask 路由，負責接收 HTTP 請求、呼叫 Model、選擇模板回傳。

---

## 2. 專案資料夾結構

```
Handsome-guy/
├── app.py                     ← Flask 應用程式入口點
├── requirements.txt           ← Python 套件依賴清單
├── .env.example               ← 環境變數範例
├── .gitignore                 ← Git 忽略規則
│
├── app/                       ← 主要應用程式資料夾
│   ├── __init__.py            ← App 初始化（Flask app factory）
│   │
│   ├── models/                ← 資料庫模型（Model 層）
│   │   ├── __init__.py
│   │   ├── user.py            ← 使用者模型（註冊/登入/角色管理）
│   │   ├── reminder.py        ← 事項提醒模型
│   │   ├── daily_report.py    ← 每日回報模型
│   │   └── emergency.py       ← 緊急通報模型
│   │
│   ├── routes/                ← Flask 路由（Controller 層）
│   │   ├── __init__.py
│   │   ├── auth.py            ← 認證路由（註冊/登入/登出）
│   │   ├── elder.py           ← 長者功能路由（回報/緊急按鈕/查看提醒）
│   │   ├── family.py          ← 家屬功能路由（儀表板/管理提醒/查看紀錄）
│   │   └── main.py            ← 通用路由（首頁/關於）
│   │
│   ├── templates/             ← Jinja2 HTML 模板（View 層）
│   │   ├── base.html          ← 基礎模板（導覽列 + 共用結構）
│   │   ├── index.html         ← 首頁
│   │   │
│   │   ├── auth/              ← 認證相關頁面
│   │   │   ├── login.html     ← 登入頁
│   │   │   └── register.html  ← 註冊頁
│   │   │
│   │   ├── elder/             ← 長者功能頁面
│   │   │   ├── dashboard.html ← 長者主頁（大按鈕介面）
│   │   │   ├── reminders.html ← 長者查看提醒
│   │   │   └── report.html    ← 每日回報頁面
│   │   │
│   │   └── family/            ← 家屬功能頁面
│   │       ├── dashboard.html ← 家屬儀表板
│   │       ├── reminders.html ← 管理提醒事項
│   │       ├── reminder_form.html ← 新增/編輯提醒表單
│   │       ├── reports.html   ← 查看回報紀錄
│   │       └── emergencies.html ← 查看緊急通報紀錄
│   │
│   └── static/                ← 靜態資源
│       ├── css/
│       │   └── style.css      ← 自訂樣式
│       └── js/
│           └── main.js        ← 自訂 JavaScript
│
├── database/                  ← 資料庫相關
│   └── schema.sql             ← SQL 建表語法
│
├── instance/                  ← Flask 實例資料夾（不納入版控）
│   └── database.db            ← SQLite 資料庫檔案
│
└── docs/                      ← 設計文件
    ├── PRD.md                 ← 產品需求文件
    ├── ARCHITECTURE.md        ← 系統架構文件（本文件）
    ├── FLOWCHART.md           ← 流程圖
    ├── DB_DESIGN.md           ← 資料庫設計
    └── ROUTES.md              ← 路由設計
```

### 各資料夾說明

| 路徑 | 用途 |
| :--- | :--- |
| `app.py` | 應用程式入口，引入 Flask app 並啟動伺服器 |
| `app/__init__.py` | Flask app factory，初始化 app、註冊 Blueprint、設定 secret key |
| `app/models/` | 每個檔案對應一張資料表，提供 CRUD 方法 |
| `app/routes/` | 每個檔案是一個 Flask Blueprint，負責處理 HTTP 請求 |
| `app/templates/` | Jinja2 模板，所有頁面都繼承 `base.html` |
| `app/static/` | CSS、JavaScript 等靜態檔案 |
| `database/schema.sql` | 完整的 SQL 建表語法，用於初始化資料庫 |
| `instance/` | SQLite 資料庫實際檔案存放處 |

---

## 3. 元件關係圖

```mermaid
flowchart TB
    subgraph 使用者
        Elder["👴 長者"]
        Family["👨‍👩‍👧 家屬"]
        Nurse["🏥 護工"]
    end

    subgraph 瀏覽器
        Browser["HTML / CSS / JS"]
    end

    subgraph "Flask 後端"
        direction TB
        AuthRoute["auth.py<br/>註冊/登入/登出"]
        ElderRoute["elder.py<br/>回報/緊急按鈕"]
        FamilyRoute["family.py<br/>儀表板/管理提醒"]
        MainRoute["main.py<br/>首頁"]
    end

    subgraph "Model 層"
        UserModel["user.py"]
        ReminderModel["reminder.py"]
        DailyReportModel["daily_report.py"]
        EmergencyModel["emergency.py"]
    end

    subgraph "資料庫"
        DB[("SQLite<br/>database.db")]
    end

    Elder --> Browser
    Family --> Browser
    Nurse --> Browser

    Browser <--> AuthRoute
    Browser <--> ElderRoute
    Browser <--> FamilyRoute
    Browser <--> MainRoute

    AuthRoute --> UserModel
    ElderRoute --> DailyReportModel
    ElderRoute --> EmergencyModel
    ElderRoute --> ReminderModel
    FamilyRoute --> ReminderModel
    FamilyRoute --> DailyReportModel
    FamilyRoute --> EmergencyModel

    UserModel --> DB
    ReminderModel --> DB
    DailyReportModel --> DB
    EmergencyModel --> DB
```

### 請求處理流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route
    participant Model as Model
    participant DB as SQLite

    User->>Browser: 點擊按鈕/送出表單
    Browser->>Route: HTTP Request (GET/POST)
    Route->>Model: 呼叫 CRUD 方法
    Model->>DB: SQL 查詢/寫入
    DB-->>Model: 查詢結果
    Model-->>Route: 回傳資料
    Route->>Route: 選擇 Jinja2 模板
    Route-->>Browser: 渲染後的 HTML
    Browser-->>User: 顯示頁面
```

---

## 4. 關鍵設計決策

### 決策 1：角色分流的介面設計

**決定**：長者和家屬/護工使用**不同的介面與路由**，而非統一介面。

**原因**：
- 長者介面需要極度簡化（大按鈕、大字體、最少操作步驟）
- 家屬/護工需要資訊豐富的儀表板
- 兩種需求差異太大，統一設計反而降低體驗

### 決策 2：使用 Flask Blueprint 組織路由

**決定**：以使用者角色為單位拆分 Blueprint（auth / elder / family / main）。

**原因**：
- 方便團隊分工，每個人負責不同模組
- 路由邏輯不會混在一起，易於維護
- 日後擴充新角色功能時不影響現有模組

### 決策 3：使用原生 sqlite3 而非 SQLAlchemy

**決定**：直接使用 Python 內建的 `sqlite3` 模組操作資料庫。

**原因**：
- 團隊成員對 SQL 語法較熟悉
- 減少學習成本，不需額外學習 ORM
- 專案規模小，ORM 的優勢不明顯

### 決策 4：不使用前後端分離

**決定**：頁面由 Flask + Jinja2 直接渲染，不使用 API + 前端框架。

**原因**：
- 課堂規定使用 Flask + Jinja2
- 團隊規模與時程適合 Server-Side Rendering
- 降低複雜度，專注在功能實作

### 決策 5：密碼安全使用 Werkzeug

**決定**：使用 Flask 內建的 `werkzeug.security` 模組的 `generate_password_hash` / `check_password_hash` 處理密碼。

**原因**：
- 不需額外安裝套件
- 預設使用 PBKDF2 演算法，安全性足夠
- 使用簡單，適合教學專案

---

*下一步：請執行 Flowchart Skill 產出流程圖文件。*
