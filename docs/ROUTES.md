# 路由設計文件 (API Design)：獨居老人生活管家系統

本文件基於 PRD、架構文件與資料庫設計，規劃系統的所有 Flask 路由與對應的 Jinja2 模板。

## 1. 路由總覽表格

| 功能模組 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| **Auth** | GET | `/auth/register` | `auth/register.html` | 顯示註冊表單 |
| **Auth** | POST | `/auth/register` | — | 接收註冊資料、寫入 DB，重導向到登入 |
| **Auth** | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| **Auth** | POST | `/auth/login` | — | 驗證帳密，設定 session，依據 role 重導向 |
| **Auth** | GET | `/auth/logout` | — | 清除 session，重導向至登入頁面 |
| **Elder** | GET | `/elder/dashboard` | `elder/dashboard.html` | 顯示長者首頁（含大字體提醒、平安打卡與 SOS 按鈕） |
| **Elder** | POST | `/elder/checkin` | — | 新增平安打卡紀錄，重導向回首頁 |
| **Elder** | POST | `/elder/sos` | — | 新增 SOS 紀錄，重導向回首頁並顯示提示 |
| **Family**| GET | `/family/dashboard` | `family/dashboard.html`| 顯示綁定長者清單與今日狀態 |
| **Family**| GET | `/family/bind` | `family/bind.html` | 顯示輸入長者綁定碼的表單 |
| **Family**| POST | `/family/bind` | — | 處理綁定邏輯，重導向回首頁 |
| **Family**| GET | `/family/reminders` | `family/reminders.html`| 顯示管理提醒事項清單 |
| **Family**| POST | `/family/reminders` | — | 接收表單新增提醒，重導向回列表 |
| **Family**| POST | `/family/reminders/<id>/toggle`| — | 啟用或停用提醒，重導向回列表 |
| **Family**| POST | `/family/reminders/<id>/delete`| — | 刪除提醒，重導向回列表 |

---

## 2. 路由詳細說明

### Auth 認證相關 ( Blueprint: `auth` )

#### 1. 註冊頁面 (`GET /auth/register`)
- **輸出**：渲染 `auth/register.html`

#### 2. 處理註冊 (`POST /auth/register`)
- **輸入**：表單欄位 `username`, `password`, `display_name`, `role`, `phone`
- **邏輯**：
  - 驗證必填與是否重複
  - 若 `role == 'elder'`，隨機產生一組 `elder_code`
  - 密碼經過 Hash 處理
  - 呼叫 `user.create_user()` 寫入資料庫
- **輸出**：重導向至 `auth.login`，失敗則 flash 錯誤並重導向 `auth.register`

#### 3. 處理登入 (`POST /auth/login`)
- **輸入**：表單欄位 `username`, `password`
- **邏輯**：驗證密碼，成功則寫入 `session['user_id']` 與 `session['role']`
- **輸出**：依據 role 分別重導向至 `elder.dashboard` 或 `family.dashboard`

### Elder 長者操作 ( Blueprint: `elder` )

#### 1. 長者首頁 (`GET /elder/dashboard`)
- **邏輯**：
  - 檢查 Session 登入狀態與身份 (限 elder)
  - 查詢今日是否已打卡 `status.get_today_checkin()`
  - 查詢今日提醒事項 `reminder.get_reminders_by_elder()`
- **輸出**：渲染 `elder/dashboard.html`，傳入紀錄與提醒資料

#### 2. 平安打卡 (`POST /elder/checkin`)
- **邏輯**：呼叫 `status.create_status_record(user_id, 'CHECKIN')`
- **輸出**：重導向 `elder.dashboard` 並 flash 成功訊息

#### 3. 緊急求助 (`POST /elder/sos`)
- **邏輯**：呼叫 `status.create_status_record(user_id, 'SOS')`，未來可在此擴充發送 Line/Email 邏輯
- **輸出**：重導向 `elder.dashboard` 並 flash「已通知聯絡人」

### Family 家屬操作 ( Blueprint: `family` )

#### 1. 綁定長者 (`POST /family/bind`)
- **輸入**：表單欄位 `elder_code`
- **邏輯**：
  - 透過 `user.get_user_by_elder_code()` 找尋長者
  - 呼叫 `user.bind_elder_to_family()` 建立關聯
- **輸出**：重導向 `family.dashboard` 並 flash 綁定結果

#### 2. 提醒事項狀態切換 (`POST /family/reminders/<id>/toggle`)
- **邏輯**：切換該 reminder_id 的 `is_active` 狀態 (0 或 1)
- **輸出**：重導向 `family.reminders`

---

## 3. Jinja2 模板清單

### 共用與認證
1. `templates/base.html`: 根骨架，包含全域 CSS/JS 引用
2. `templates/auth/login.html`: 登入表單 (繼承 base.html)
3. `templates/auth/register.html`: 註冊表單 (繼承 base.html)

### 長者端
4. `templates/elder/base.html`: 長者專用極簡骨架 (繼承 base.html)
5. `templates/elder/dashboard.html`: 首頁，包含超大字體、高對比度的打卡與 SOS 按鈕 (繼承 elder/base.html)

### 家屬/護工端
6. `templates/family/base.html`: 家屬專用骨架，包含左側/上方完整導覽列 (繼承 base.html)
7. `templates/family/dashboard.html`: 儀表板，顯示綁定的長者狀態清單 (繼承 family/base.html)
8. `templates/family/bind.html`: 綁定新長者的畫面 (繼承 family/base.html)
9. `templates/family/reminders.html`: 建立與管理提醒事項的畫面 (繼承 family/base.html)

---

## 4. 路由骨架程式碼
請參考 `app/routes/` 內的 Python 檔案，包含：
- `__init__.py`
- `auth.py`
- `elder.py`
- `family.py`
