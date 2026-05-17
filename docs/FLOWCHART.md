# 流程圖設計 (Flowchart)：獨居老人生活管家系統

本文件基於 PRD 與系統架構設計，視覺化了使用者的操作路徑與系統內部的資料流動。

## 1. 使用者流程圖 (User Flow)

展示兩種主要目標用戶（長者、家屬/護工）在系統中的核心操作路徑：

```mermaid
flowchart LR
    A([使用者開啟系統]) --> B{選擇登入身分}
    
    B -->|長者登入| C[長者專用首頁 dashboard]
    B -->|家屬/護工登入| D[家屬管理首頁 dashboard]
    
    %% 長者操作路徑
    C --> E[點擊『我很好 平安回報』]
    C --> F[點擊『SOS 緊急求助』]
    C --> G[查看『今日事項提醒』]
    
    E --> K([顯示打卡成功提示])
    F --> L([顯示已通報聯絡人])
    
    %% 家屬/護工操作路徑
    D --> H[查看長者今日回報狀態與歷史]
    D --> I[設定長者用藥/日常提醒]
    D --> J[管理帳號綁定與緊急聯絡人設定]
    
    I --> M([填寫提醒時間與內容])
    J --> N([輸入長者代碼進行綁定])
```

---

## 2. 系統序列圖 (Sequence Diagram)

以系統最核心的**「長者點擊 SOS 緊急求助」**功能為例，展示從使用者點擊到資料庫儲存的完整流程：

```mermaid
sequenceDiagram
    actor Elder as 獨居老人
    participant Browser as 瀏覽器 (前端)
    participant Route as Flask 路由 (elder.py)
    participant Model as Model (status.py)
    participant DB as SQLite 資料庫
    
    Elder->>Browser: 點擊大字體的「SOS 緊急求助」按鈕
    Browser->>Route: 發送請求: POST /elder/sos
    
    Route->>Model: 呼叫建立緊急狀態紀錄邏輯
    Model->>DB: 執行 SQL: INSERT INTO status (type='SOS')
    DB-->>Model: 回傳儲存成功
    Model-->>Route: 取得新增的紀錄 ID
    
    Note over Route: 路由層可在此處觸發外部通知 API<br/>(例如 Email、LINE Notify) 通知家屬
    
    Route-->>Browser: HTTP 302 重導向回 /elder/dashboard
    Browser-->>Elder: 重新渲染首頁，並顯示「已通知聯絡人」的明顯提示
```

---

## 3. 功能清單與路由對照表

以下整理了系統主要功能、對應負責的角色、預計的 URL 路徑及 HTTP 方法：

| 功能名稱 | 目標角色 | URL 路徑 | HTTP 方法 | 說明 |
| --- | --- | --- | --- | --- |
| **註冊與登入** | 共用 | `/auth/login` <br> `/auth/register` | GET, POST | 處理帳號認證，登入後根據角色導向不同首頁 |
| **長者首頁** | 長者 | `/elder/dashboard` | GET | 渲染極簡大字體介面，顯示提醒事項與操作按鈕 |
| **平安回報** | 長者 | `/elder/checkin` | POST | 接收長者的平安打卡，紀錄時間與狀態 |
| **緊急求助 (SOS)** | 長者 | `/elder/sos` | POST | 接收緊急求助訊號，寫入資料庫並可觸發通知 |
| **家屬首頁** | 家屬/護工 | `/family/dashboard` | GET | 顯示已綁定長者的回報狀態總覽與歷史紀錄 |
| **設定提醒** | 家屬/護工 | `/family/reminders` | GET, POST | 列出、新增、編輯或刪除給長者的作息與用藥提醒 |
| **綁定長者** | 家屬/護工 | `/family/bind` | GET, POST | 設定緊急聯絡資訊與建立家屬、長者間的關聯 |
