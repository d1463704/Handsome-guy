# 獨居老人生活管家 — 路由設計

> **對應文件**：[PRD](./PRD.md) / [Architecture](./ARCHITECTURE.md) / [DB Design](./DB_DESIGN.md)  
> **版本**：v1.0  
> **最後更新**：2026-05-19

---

## 1. 路由總覽表格

### 通用路由（main）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 首頁 | GET | `/` | `index.html` | 系統介紹頁，含登入/註冊入口 |

### 認證路由（auth）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 登入頁 | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| 登入處理 | POST | `/auth/login` | — | 驗證帳密，成功則設定 session 並重導向 |
| 註冊頁 | GET | `/auth/register` | `auth/register.html` | 顯示註冊表單 |
| 註冊處理 | POST | `/auth/register` | — | 建立帳號，重導向登入頁 |
| 登出 | GET | `/auth/logout` | — | 清除 session，重導向首頁 |

### 長者路由（elder）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 長者主頁 | GET | `/elder/dashboard` | `elder/dashboard.html` | 大按鈕介面 |
| 每日回報 | POST | `/elder/daily-report` | — | 記錄回報，重導向主頁 |
| 緊急求助 | POST | `/elder/emergency` | — | 產生緊急通報，重導向主頁 |
| 查看提醒 | GET | `/elder/reminders` | `elder/reminders.html` | 顯示今日提醒列表 |
| 標記提醒完成 | POST | `/elder/reminders/<id>/complete` | — | 更新狀態，重導向提醒頁 |

### 家屬路由（family）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 家屬儀表板 | GET | `/family/dashboard` | `family/dashboard.html` | 長者狀態總覽 |
| 提醒列表 | GET | `/family/reminders` | `family/reminders.html` | 管理所有提醒 |
| 新增提醒頁 | GET | `/family/reminders/new` | `family/reminder_form.html` | 顯示新增表單 |
| 建立提醒 | POST | `/family/reminders` | — | 儲存新提醒，重導向列表 |
| 編輯提醒頁 | GET | `/family/reminders/<id>/edit` | `family/reminder_form.html` | 顯示編輯表單 |
| 更新提醒 | POST | `/family/reminders/<id>/update` | — | 更新提醒，重導向列表 |
| 刪除提醒 | POST | `/family/reminders/<id>/delete` | — | 刪除提醒，重導向列表 |
| 回報紀錄 | GET | `/family/reports` | `family/reports.html` | 查看長者回報歷史 |
| 緊急通報紀錄 | GET | `/family/emergencies` | `family/emergencies.html` | 查看緊急通報歷史 |
| 處理通報 | POST | `/family/emergencies/<id>/resolve` | — | 標記通報已處理 |
| 綁定長者頁 | GET | `/family/link` | `family/link.html` | 顯示綁定表單 |
| 綁定長者 | POST | `/family/link` | — | 建立綁定關係 |

---

## 2. 每個路由的詳細說明

### 2.1 通用路由 — `app/routes/main.py`

#### `GET /`
- **輸入**：無
- **處理邏輯**：
  1. 如果使用者已登入，依角色重導向到對應儀表板
  2. 否則渲染首頁
- **輸出**：渲染 `index.html`
- **錯誤處理**：無

---

### 2.2 認證路由 — `app/routes/auth.py`

#### `GET /auth/login`
- **輸入**：無
- **處理邏輯**：顯示登入表單
- **輸出**：渲染 `auth/login.html`

#### `POST /auth/login`
- **輸入**：表單欄位 `username`, `password`
- **處理邏輯**：
  1. 驗證必填欄位
  2. 呼叫 `User.get_by_username(username)`
  3. 使用 `check_password_hash()` 驗證密碼
  4. 成功：設定 `session['user_id']` 和 `session['role']`
  5. 依角色重導向：長者 → `/elder/dashboard`，家屬 → `/family/dashboard`
- **輸出**：重導向到對應儀表板
- **錯誤處理**：帳號不存在或密碼錯誤 → flash 錯誤訊息，回到登入頁

#### `GET /auth/register`
- **輸入**：無
- **處理邏輯**：顯示註冊表單
- **輸出**：渲染 `auth/register.html`

#### `POST /auth/register`
- **輸入**：表單欄位 `username`, `password`, `confirm_password`, `display_name`, `role`, `phone`
- **處理邏輯**：
  1. 驗證必填欄位（username, password, display_name, role）
  2. 驗證密碼與確認密碼是否相符
  3. 檢查 username 是否已存在
  4. 使用 `generate_password_hash()` 雜湊密碼
  5. 呼叫 `User.create(data)` 建立帳號
- **輸出**：重導向到 `/auth/login`，flash 成功訊息
- **錯誤處理**：帳號重複 → flash 錯誤訊息，回到註冊頁

#### `GET /auth/logout`
- **輸入**：無
- **處理邏輯**：清除 session
- **輸出**：重導向到 `/`

---

### 2.3 長者路由 — `app/routes/elder.py`

> ⚠️ 所有長者路由需驗證 `session['role'] == 'elder'`

#### `GET /elder/dashboard`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 查詢今日是否已回報：`DailyReport.get_today(user_id)`
  2. 查詢今日待完成提醒數：`Reminder.get_pending_count(user_id)`
- **輸出**：渲染 `elder/dashboard.html`，傳入 `reported_today`, `pending_count`

#### `POST /elder/daily-report`
- **輸入**：`session['user_id']`，表單欄位 `status`（預設 safe）
- **處理邏輯**：
  1. 呼叫 `DailyReport.create(user_id, status)`
- **輸出**：重導向到 `/elder/dashboard`，flash 成功訊息
- **錯誤處理**：今日已回報 → flash 提示

#### `POST /elder/emergency`
- **輸入**：`session['user_id']`，表單欄位 `message`（可選）
- **處理邏輯**：
  1. 呼叫 `Emergency.create(user_id, message)`
- **輸出**：重導向到 `/elder/dashboard`，flash「已通知家屬」

#### `GET /elder/reminders`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 呼叫 `Reminder.get_by_elder(user_id)` 取得今日提醒
- **輸出**：渲染 `elder/reminders.html`，傳入 `reminders`

#### `POST /elder/reminders/<id>/complete`
- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `Reminder.update(id, {'status': 'completed'})`
- **輸出**：重導向到 `/elder/reminders`
- **錯誤處理**：id 不存在 → 404

---

### 2.4 家屬路由 — `app/routes/family.py`

> ⚠️ 所有家屬路由需驗證 `session['role'] in ['family', 'nurse']`

#### `GET /family/dashboard`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 取得綁定的長者列表：`ElderFamilyLink.get_elders(family_id)`
  2. 對每位長者查詢今日回報狀態、待完成提醒、未處理緊急通報
- **輸出**：渲染 `family/dashboard.html`，傳入 `elders_status`

#### `GET /family/reminders`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 取得綁定長者的所有提醒：`Reminder.get_by_family(family_id)`
- **輸出**：渲染 `family/reminders.html`，傳入 `reminders`

#### `GET /family/reminders/new`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 取得綁定的長者列表（供選擇）
- **輸出**：渲染 `family/reminder_form.html`，傳入 `elders`, `reminder=None`

#### `POST /family/reminders`
- **輸入**：表單欄位 `elder_id`, `title`, `description`, `remind_time`, `repeat_type`, `due_date`
- **處理邏輯**：
  1. 驗證必填欄位（elder_id, title, remind_time）
  2. 呼叫 `Reminder.create(data)`
- **輸出**：重導向到 `/family/reminders`
- **錯誤處理**：驗證失敗 → flash 錯誤，回到表單頁

#### `GET /family/reminders/<id>/edit`
- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `Reminder.get_by_id(id)` 取得既有資料
- **輸出**：渲染 `family/reminder_form.html`，傳入 `reminder`
- **錯誤處理**：id 不存在 → 404

#### `POST /family/reminders/<id>/update`
- **輸入**：URL 參數 `id`，表單欄位同新增
- **處理邏輯**：
  1. 驗證必填欄位
  2. 呼叫 `Reminder.update(id, data)`
- **輸出**：重導向到 `/family/reminders`
- **錯誤處理**：id 不存在 → 404

#### `POST /family/reminders/<id>/delete`
- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `Reminder.delete(id)`
- **輸出**：重導向到 `/family/reminders`
- **錯誤處理**：id 不存在 → 404

#### `GET /family/reports`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 取得綁定長者的回報紀錄：`DailyReport.get_by_family(family_id)`
- **輸出**：渲染 `family/reports.html`，傳入 `reports`

#### `GET /family/emergencies`
- **輸入**：`session['user_id']`
- **處理邏輯**：
  1. 取得綁定長者的緊急通報：`Emergency.get_by_family(family_id)`
- **輸出**：渲染 `family/emergencies.html`，傳入 `emergencies`

#### `POST /family/emergencies/<id>/resolve`
- **輸入**：URL 參數 `id`，`session['user_id']`
- **處理邏輯**：
  1. 呼叫 `Emergency.resolve(id, resolved_by=user_id)`
- **輸出**：重導向到 `/family/emergencies`

#### `GET /family/link`
- **輸入**：`session['user_id']`
- **處理邏輯**：顯示綁定長者表單
- **輸出**：渲染 `family/link.html`

#### `POST /family/link`
- **輸入**：表單欄位 `elder_username`
- **處理邏輯**：
  1. 查詢長者帳號是否存在且角色為 elder
  2. 檢查是否已綁定
  3. 呼叫 `ElderFamilyLink.create(elder_id, family_id)`
- **輸出**：重導向到 `/family/dashboard`
- **錯誤處理**：帳號不存在或角色不對 → flash 錯誤
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

所有模板都繼承 `base.html`。

| 模板路徑 | 繼承 | 說明 |
| :--- | :--- | :--- |
| `templates/base.html` | — | 基礎模板：HTML head、Bootstrap CDN、導覽列、flash message、content block |
| `templates/index.html` | `base.html` | 首頁：系統介紹、登入/註冊按鈕 |
| `templates/auth/login.html` | `base.html` | 登入表單 |
| `templates/auth/register.html` | `base.html` | 註冊表單（含角色選擇） |
| `templates/elder/dashboard.html` | `base.html` | 長者主頁：三個大按鈕（我很好/緊急求助/查看提醒） |
| `templates/elder/reminders.html` | `base.html` | 長者提醒列表 |
| `templates/family/dashboard.html` | `base.html` | 家屬儀表板：長者狀態卡片 |
| `templates/family/reminders.html` | `base.html` | 提醒管理列表 |
| `templates/family/reminder_form.html` | `base.html` | 新增/編輯提醒表單 |
| `templates/family/reports.html` | `base.html` | 回報紀錄列表 |
| `templates/family/emergencies.html` | `base.html` | 緊急通報紀錄 |
| `templates/family/link.html` | `base.html` | 綁定長者表單 |

---

## 4. 路由骨架程式碼

路由骨架將建立在 `app/routes/` 資料夾中，每個 Blueprint 對應一個 `.py` 檔案。

> 骨架程式碼將在 Implementation 階段實作。

---

*下一步：請執行 Implementation Skill 開始實作程式碼。*
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
