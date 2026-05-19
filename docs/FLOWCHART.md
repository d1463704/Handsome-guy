# 獨居老人生活管家 — 流程圖設計

> **對應文件**：[PRD](./PRD.md) / [Architecture](./ARCHITECTURE.md)  
> **版本**：v1.0  
> **最後更新**：2026-05-19

---

## 1. 使用者流程圖（User Flow）

### 1.1 整體系統流程

```mermaid
flowchart TB
    A([使用者開啟網頁]) --> B{是否已登入?}
    B -->|否| C[登入頁面]
    C --> D{有帳號嗎?}
    D -->|否| E[註冊頁面]
    E --> F[選擇角色: 長者/家屬/護工]
    F --> G[填寫註冊資訊]
    G --> C
    D -->|是| H[輸入帳號密碼]
    H --> I{登入成功?}
    I -->|否| C
    I -->|是| J{判斷角色}
    B -->|是| J

    J -->|長者| K["長者主頁 (大按鈕介面)"]
    J -->|家屬| L["家屬儀表板"]
    J -->|護工| M["護工儀表板"]
```

### 1.2 長者操作流程

```mermaid
flowchart TB
    K["長者主頁"] --> K1["🟢 我很好 (每日回報)"]
    K --> K2["🔴 緊急求助"]
    K --> K3["📋 查看提醒"]
    K --> K4["🚪 登出"]

    K1 --> K1a["按下按鈕"]
    K1a --> K1b["系統記錄回報時間"]
    K1b --> K1c["顯示: 今日已回報 ✓"]

    K2 --> K2a["按下緊急按鈕"]
    K2a --> K2b["系統產生緊急通報"]
    K2b --> K2c["顯示: 已通知家屬"]

    K3 --> K3a["查看今日提醒列表"]
    K3a --> K3b{有待完成項目?}
    K3b -->|是| K3c["按下「已完成」"]
    K3c --> K3d["更新提醒狀態"]
    K3b -->|否| K3e["顯示: 全部完成 🎉"]
```

### 1.3 家屬操作流程

```mermaid
flowchart TB
    L["家屬儀表板"] --> L1["📊 查看長者狀態"]
    L --> L2["⏰ 管理提醒事項"]
    L --> L3["📝 查看回報紀錄"]
    L --> L4["🚨 查看緊急通報"]
    L --> L5["🚪 登出"]

    L1 --> L1a["今日回報狀態 / 提醒完成度 / 緊急通報"]

    L2 --> L2a{操作選擇}
    L2a -->|新增| L2b["填寫提醒表單"]
    L2b --> L2c["設定內容/時間/重複"]
    L2c --> L2d["儲存到資料庫"]
    L2a -->|編輯| L2e["修改提醒內容"]
    L2e --> L2d
    L2a -->|刪除| L2f["確認刪除"]
    L2f --> L2g["從資料庫移除"]

    L3 --> L3a["查看長者回報歷史"]
    L4 --> L4a["查看緊急通報歷史"]
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 使用者註冊流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as User Model
    participant DB as SQLite

    User->>Browser: 點擊「註冊」
    Browser->>Flask: GET /auth/register
    Flask-->>Browser: 回傳註冊表單頁面

    User->>Browser: 填寫帳號/密碼/角色 並送出
    Browser->>Flask: POST /auth/register
    Flask->>Flask: 驗證輸入資料
    Flask->>Model: create(username, password_hash, role)
    Model->>DB: INSERT INTO users
    DB-->>Model: 成功
    Model-->>Flask: 回傳新使用者
    Flask-->>Browser: 重導向到登入頁
```

### 2.2 使用者登入流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as User Model
    participant DB as SQLite

    User->>Browser: 輸入帳號密碼
    Browser->>Flask: POST /auth/login
    Flask->>Model: get_by_username(username)
    Model->>DB: SELECT * FROM users WHERE username=?
    DB-->>Model: 使用者資料
    Model-->>Flask: 回傳使用者
    Flask->>Flask: check_password_hash(password)
    alt 密碼正確
        Flask->>Flask: 設定 session
        Flask-->>Browser: 重導向到對應儀表板
    else 密碼錯誤
        Flask-->>Browser: 顯示錯誤訊息
    end
```

### 2.3 每日回報流程

```mermaid
sequenceDiagram
    actor Elder as 長者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as DailyReport Model
    participant DB as SQLite

    Elder->>Browser: 按下「我很好」按鈕
    Browser->>Flask: POST /elder/daily-report
    Flask->>Flask: 取得 session 中的 user_id
    Flask->>Model: create(user_id, status="safe")
    Model->>DB: INSERT INTO daily_reports
    DB-->>Model: 成功
    Model-->>Flask: 回傳新紀錄
    Flask-->>Browser: 顯示「今日已回報 ✓」
```

### 2.4 緊急按鈕流程

```mermaid
sequenceDiagram
    actor Elder as 長者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Emergency Model
    participant DB as SQLite

    Elder->>Browser: 按下緊急求助按鈕
    Browser->>Flask: POST /elder/emergency
    Flask->>Flask: 取得 session 中的 user_id
    Flask->>Model: create(user_id, message)
    Model->>DB: INSERT INTO emergencies
    DB-->>Model: 成功
    Model-->>Flask: 回傳通報紀錄
    Flask-->>Browser: 顯示「已通知家屬」確認頁面
```

### 2.5 新增事項提醒流程

```mermaid
sequenceDiagram
    actor Family as 家屬
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Reminder Model
    participant DB as SQLite

    Family->>Browser: 點擊「新增提醒」
    Browser->>Flask: GET /family/reminders/new
    Flask-->>Browser: 回傳提醒表單頁面

    Family->>Browser: 填寫提醒內容/時間 並送出
    Browser->>Flask: POST /family/reminders
    Flask->>Flask: 驗證表單資料
    Flask->>Model: create(elder_id, title, time, repeat)
    Model->>DB: INSERT INTO reminders
    DB-->>Model: 成功
    Model-->>Flask: 回傳新提醒
    Flask-->>Browser: 重導向到提醒列表頁
```

---

## 3. 功能清單對照表

| 功能 | URL 路徑 | HTTP 方法 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 首頁 | `/` | GET | `index.html` | 系統介紹與登入入口 |
| 登入頁 | `/auth/login` | GET | `auth/login.html` | 顯示登入表單 |
| 登入處理 | `/auth/login` | POST | — | 驗證帳密，設定 session |
| 註冊頁 | `/auth/register` | GET | `auth/register.html` | 顯示註冊表單 |
| 註冊處理 | `/auth/register` | POST | — | 建立帳號，重導向登入頁 |
| 登出 | `/auth/logout` | GET | — | 清除 session，重導向首頁 |
| 長者主頁 | `/elder/dashboard` | GET | `elder/dashboard.html` | 顯示大按鈕介面 |
| 每日回報 | `/elder/daily-report` | POST | — | 記錄今日回報 |
| 緊急求助 | `/elder/emergency` | POST | — | 產生緊急通報 |
| 長者查看提醒 | `/elder/reminders` | GET | `elder/reminders.html` | 顯示今日提醒 |
| 標記提醒完成 | `/elder/reminders/<id>/complete` | POST | — | 更新提醒狀態 |
| 家屬儀表板 | `/family/dashboard` | GET | `family/dashboard.html` | 顯示長者狀態總覽 |
| 提醒列表 | `/family/reminders` | GET | `family/reminders.html` | 管理所有提醒 |
| 新增提醒頁 | `/family/reminders/new` | GET | `family/reminder_form.html` | 顯示新增表單 |
| 建立提醒 | `/family/reminders` | POST | — | 儲存新提醒 |
| 編輯提醒頁 | `/family/reminders/<id>/edit` | GET | `family/reminder_form.html` | 顯示編輯表單 |
| 更新提醒 | `/family/reminders/<id>/update` | POST | — | 更新提醒內容 |
| 刪除提醒 | `/family/reminders/<id>/delete` | POST | — | 刪除提醒 |
| 查看回報紀錄 | `/family/reports` | GET | `family/reports.html` | 查看長者回報歷史 |
| 查看緊急通報 | `/family/emergencies` | GET | `family/emergencies.html` | 查看緊急通報歷史 |

---

*下一步：請執行 DB Design Skill 產出資料庫設計文件。*
