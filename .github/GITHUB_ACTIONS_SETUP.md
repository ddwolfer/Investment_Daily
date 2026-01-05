# GitHub Actions 部署設定指南

本文件詳細說明如何在 GitHub Actions 上設定自動化執行投資日報機器人。

---

## 📋 前置準備

### 1. 準備 Google Service Account 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立或選擇專案
3. 啟用 **Google Sheets API**
4. 建立 **Service Account** 並下載 JSON 金鑰
5. 將 JSON 檔案的**完整內容**複製（稍後會用到）

### 2. 準備 API Keys

- **Telegram Bot Token**: 與 [@BotFather](https://t.me/BotFather) 對話建立 Bot
- **Telegram Chat ID**: 發訊給 Bot 後用 [getUpdates API](https://api.telegram.org/bot<token>/getUpdates) 查詢
- **Telegram Topic ID** (可選): 執行 `test_script/get_topic_id.py` 取得
- **Gemini API Key**: 到 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得

### 3. 準備 Google Sheet IDs

從試算表網址複製 Sheet ID：
- 格式：`https://docs.google.com/spreadsheets/d/{THIS_IS_ID}/edit`
- 需要兩個 Sheet ID：美股和加密貨幣

---

## 🔐 設定 GitHub Secrets

### 步驟 1：進入 Repository Settings

1. 前往你的 GitHub Repository
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **New repository secret**

### 步驟 2：新增所有必要的 Secrets

請依序新增以下 Secrets（**名稱必須完全一致**）：

#### Telegram Bot 設定

| Secret 名稱 | 說明 | 範例值 |
|-------------|------|--------|
| `TELEGRAM_BOT_TOKEN` | Bot Token | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Chat ID | `123456789` |
| `TELEGRAM_TOPIC_ID` | Topic ID (可選) | `479` |

#### LLM API 設定

| Secret 名稱 | 說明 | 範例值 |
|-------------|------|--------|
| `GEMINI_API_KEY` | Gemini API Key | `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| `OPENAI_API_KEY` | OpenAI API Key (可選) | `sk-...` |

#### Google Sheets 設定

| Secret 名稱 | 說明 | 範例值 |
|-------------|------|--------|
| `GOOGLE_SHEET_ID_STOCK` | 美股試算表 ID | `1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4` |
| `GOOGLE_SHEET_ID_CRYPTO` | 加密貨幣試算表 ID | `9zY8xW7vU6tS5rQ4pO3nM2lK1jI0hG9fE8dC7bA6` |
| `GOOGLE_SHEET_RANGE` | Sheet 範圍 (可選) | `總損益!A:Z` |

#### Google Service Account 憑證

| Secret 名稱 | 說明 | 重要提示 |
|-------------|------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS_CONTENT` | **完整的 JSON 檔案內容** | ⚠️ 必須是完整的 JSON，包含所有 `{}` 和換行 |

**如何取得 `GOOGLE_APPLICATION_CREDENTIALS_CONTENT`**：

1. 下載 Service Account JSON 檔案（例如：`my-project-12345-abc.json`）
2. 用文字編輯器打開該檔案
3. **完整複製所有內容**（包括 `{`、`}`、所有欄位、換行符號）
4. 貼到 GitHub Secret 中

**範例格式**：
```json
{
  "type": "service_account",
  "project_id": "my-project-12345",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "my-service@my-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## 📝 Workflow 檔案說明

Workflow 檔案位於 `.github/workflows/daily_report.yml`，主要步驟：

### 1. 觸發條件

```yaml
on:
  schedule:
    - cron: '0 22 * * *'  # 台北時間 06:00 (UTC 22:00)
  workflow_dispatch:  # 允許手動觸發
```

- **自動執行**：每天 UTC 22:00（台北時間 06:00）
- **手動觸發**：可在 GitHub Actions 頁面手動執行

### 2. 執行步驟

1. **Checkout code**: 下載程式碼
2. **Setup uv**: 安裝 uv 套件管理器
3. **Install dependencies**: 安裝 Python 依賴
4. **Create credentials.json**: 從 Secret 建立憑證檔案
5. **Run investment bot**: 執行程式

---

## ✅ 驗證設定

### 方法 1：手動觸發測試

1. 前往 GitHub Repository → **Actions** 標籤
2. 選擇 **Daily Investment Report** workflow
3. 點擊 **Run workflow** → **Run workflow**
4. 觀察執行日誌，確認：
   - ✅ 所有 Secrets 正確讀取
   - ✅ credentials.json 成功建立
   - ✅ 程式正常執行並發送報告

### 方法 2：檢查執行日誌

在 Actions 執行日誌中，應該看到：

```
✅ credentials.json 格式驗證通過
🚀 啟動 AI 投資日報機器人...
🔧 初始化服務中...
  [GoogleSheet] 憑證檔案存在: /home/runner/work/.../credentials.json
  [GoogleSheet] 驗證成功，服務已建立。
  ...
✅ 任務完成！
```

---

## 🔧 常見問題排除

### 問題 1：credentials.json 格式錯誤

**錯誤訊息**：
```
[GoogleSheet] 憑證驗證失敗: Invalid JSON
```

**解決方案**：
- 確認 `GOOGLE_APPLICATION_CREDENTIALS_CONTENT` Secret 包含完整的 JSON 內容
- 檢查是否有遺漏 `{`、`}` 或換行符號
- 在 Workflow 中加入 JSON 驗證步驟（已包含）

### 問題 2：找不到 credentials.json

**錯誤訊息**：
```
[GoogleSheet] 憑證檔不存在: credentials.json
```

**解決方案**：
- 確認 Workflow 中的 `Create credentials.json` 步驟成功執行
- 檢查 `GOOGLE_APPLICATION_CREDENTIALS_CONTENT` Secret 是否正確設定

### 問題 3：環境變數未讀取

**錯誤訊息**：
```
[Telegram] 警告: 未設定 TELEGRAM_BOT_TOKEN
```

**解決方案**：
- 確認所有 Secrets 名稱與 Workflow 中的 `env:` 區塊完全一致
- 檢查 Secrets 是否正確設定（Settings → Secrets and variables → Actions）

### 問題 4：中文亂碼

**解決方案**：
- 確認 Workflow 中有設定 `PYTHONUTF8: 1`（已包含）

---

## 🔒 安全性提醒

1. **絕對不要**將 Secrets 寫入程式碼或 commit 到 Git
2. **確認** `.gitignore` 已包含 `.env` 和 `credentials.json`
3. **定期輪換** API Keys 和憑證（建議每 3-6 個月）
4. **限制** Service Account 權限（只給予必要的 Google Sheets 讀取權限）

---

## 📅 時區說明

- **Cron 時間**：使用 UTC 時區
- **台北時間 06:00** = **UTC 22:00**（前一日）
- 如需調整執行時間，修改 Workflow 中的 cron 表達式：
  ```yaml
  - cron: '0 22 * * *'  # 台北 06:00
  - cron: '0 8 * * *'   # 台北 16:00
  ```

---

## 🎯 下一步

設定完成後：

1. **測試執行**：手動觸發一次 Workflow 確認正常
2. **監控執行**：每天檢查 Actions 執行狀態
3. **查看報告**：確認 Telegram 收到報告

如有問題，請查看 Actions 執行日誌進行除錯。
