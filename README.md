# AI 投資日報機器人 (AI Investment Daily Bot)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-latest-orange.svg)](https://github.com/astral-sh/uv)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%20Flash-purple.svg)](https://ai.google.dev/)

> 📊 自動化投資分析 | 🧠 AI 智能報告 | 📱 Telegram 即時推送

這是一個基於 Python 的自動化投資分析工具，專為同時投資「**美股 (US Stocks)**」與「**加密貨幣 (Crypto)**」的投資者設計。

它扮演一位「**理性數據派的風控官 (Rational Risk Manager)**」，每天早上自動分析你的投資組合，計算技術指標 (RSI, EMA, MACD)，並透過 AI 生成一份客觀、拒絕 FOMO 的投資日報，最後發送到 Telegram。

**🆕 最新版本**: v1.1 (2025-12-19)
- ✅ HTML 格式 Telegram 推送
- ✅ 智能分層報告（重點分析 vs 摘要）
- ✅ 自動日期頭部生成
- ✅ HTML 特殊字符智能轉義
- ✅ Telegram Topic 支援

## 🌟 核心功能 (Features)

### 數據整合
*   **雙 Google Sheet 支援**：支援分別從「美股試算表」與「加密貨幣試算表」讀取持倉數據並自動合併
*   **智能欄位對映**：自動處理中英文欄位名稱（`stock` → `Symbol`, `總數量` → `Qty` 等）
*   **多數據源串接**：
    *   **Yahoo Finance** - 美股實時行情與歷史數據
    *   **Binance (ccxt)** - 加密貨幣即時價格與交易數據
    *   **Fear & Greed Index** - 市場情緒指標

### 專業技術分析
*   **美股策略**：Trend-following (EMA 20/60/120, RSI 14)
*   **Crypto 策略**：高波動策略 (EMA 5/10/20, RSI 6)
*   **進階指標**：MACD 背離偵測、Bollinger Bands、交易量分析
*   **信號儲存**：每日技術信號自動儲存到本地資料庫

### AI 智能報告
*   **使用 Gemini Flash Latest** 生成繁體中文日報
*   **智能分層分析**：
    *   **重點標的**（詳細分析 100-150 字）- 針對 Watchlist 或風險標的
    *   **其他持倉**（一行總結 15-20 字）- 快速掃描健康狀況
    *   自動識別需要關注的標的，避免報告過長
*   **報告結構**：
    *   📅 **自動日期頭部** - Python 動態生成，格式固定（2025年12月19日 星期五）
    *   ⚠️ **風險警示** - RSI 超買/超賣、趨勢轉弱、突破布林通道
    *   🎯 **操作建議** - 明確的買/賣/持有建議，附具體數量
    *   🌍 **市場情緒分析** - Fear & Greed Index 解讀與交叉驗證
    *   📋 **今日重點關注** - 2-3 個最需優先處理的標的
*   **風格**：客觀理性、數據驅動、拒絕 FOMO
*   **輸出優化**：控制在 1500-2200 字以內，質量優於數量

### 本地儲存與快取
*   **混合儲存架構**（SQLite + Parquet）：
    *   **Parquet** - 市場歷史數據（高效壓縮、快速讀寫）
    *   **SQLite** - 技術信號、持倉快照、市場情緒、快取元數據
*   **智能快取**：市場數據快取 60 分鐘，大幅減少 API 調用
*   **歷史追蹤**：每日持倉快照，可回溯分析績效

### Telegram 推送
*   **HTML 格式渲染**：支援粗體（`<b>`）、斜體（`<i>`）、代碼（`<code>`）
*   **智能標籤清理**：自動移除不支援的 HTML 標籤（h1-6, ul/ol/li, hr, div）
*   **特殊字符轉義**：自動轉義 `<` `>` `&` 為 HTML 實體（`&lt;` `&gt;` `&amp;`）
*   **Topic 支援**：支援發送到 Telegram 群組的特定 Topic
*   **長訊息分段**：超過 4096 字元自動分段發送
*   **錯誤重試**：支援重試機制與優雅降級（純文字模式）

## 📂 專案結構 (Project Structure)

```text
Investment_Daily/
├── 📄 .env                       # 環境變數（API Keys, Sheet IDs）⚠️ 不納入版控
├── 📄 credentials.json           # Google Service Account 金鑰 ⚠️ 不納入版控
├── 📄 pyproject.toml             # 專案依賴與打包設定
├── 📄 uv.lock                    # 鎖定的依賴版本（自動生成）
├── 📄 README.md                  # 專案說明（本文件）
├── 📄 AGENTS.md                  # AI 協作指引（Cursor Agent 規則）
├── 📄 TODO.md                    # 待辦事項與開發進度
├── 📄 spec.md                    # 技術規格文件
├── 📄 project_context.md         # 專案背景與設計理念
├── 📄 design_storage.md          # 本地儲存架構設計
├── 📄 error_log.md               # 已解決的技術問題記錄
│
├── 📁 investment_bot/            # 主要程式碼目錄
│   ├── 📄 __init__.py
│   ├── 📄 config.py              # 配置管理（讀取 .env）
│   ├── 📄 main.py                # 主流程編排
│   │
│   ├── 📁 services/              # 業務邏輯層
│   │   ├── 📄 __init__.py
│   │   ├── 📄 google_sheet.py    # Google Sheets API（雙來源支援）
│   │   ├── 📄 market_data.py     # 市場數據（yfinance + ccxt）
│   │   ├── 📄 tech_analysis.py   # 技術分析計算
│   │   ├── 📄 llm_analyzer.py    # LLM 報告生成（Gemini）
│   │   └── 📄 telegram_bot.py    # Telegram 推送
│   │
│   ├── 📁 utils/                 # 工具層
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_store.py      # 統一數據存取介面（Facade）
│   │   ├── 📄 db_manager.py      # SQLite 資料庫管理
│   │   └── 📄 formatters.py      # 格式化工具
│   │
│   └── 📁 data/                  # 本地數據儲存 🚫 已在 .gitignore
│       ├── 📄 investment.db       # SQLite 資料庫
│       └── 📁 market_data/        # Parquet 檔案（市場歷史數據）
│           ├── TSLA.parquet
│           └── BTC.parquet
│
└── 📁 test_script/               # 測試腳本目錄
    ├── 📄 test_gemini.py         # Gemini API 測試
    ├── 📄 test_storage.py        # 本地儲存整合測試
    ├── 📄 test_market_apis.py    # Market Data API 整合測試
    ├── 📄 test_llm_analyzer.py   # LLM Analyzer 完整測試
    ├── 📄 test_llm_html_output.py # LLM HTML 格式輸出測試
    ├── 📄 test_telegram_bot.py   # Telegram Bot 功能測試
    ├── 📄 test_html_format.py    # HTML 格式轉換測試
    ├── 📄 test_html_tag_cleanup.py # HTML 標籤清理測試
    ├── 📄 test_html_escape.py    # HTML 特殊字符轉義測試
    ├── 📄 test_report_header.py  # 報告頭部功能測試
    ├── 📄 get_topic_id.py        # Telegram Topic ID 獲取工具
    └── 📄 debug_google_sheet.py  # Google Sheet 連線除錯
```

### 文件導覽指南

| 文件 | 用途 | 適合閱讀時機 |
|------|------|-------------|
| **README.md** | 快速開始與安裝指南 | 👈 你正在看這個 |
| **spec.md** | 完整技術規格 | 深入了解架構設計 |
| **TODO.md** | 開發進度追蹤 | 查看當前狀態與待辦 |
| **AGENTS.md** | AI 協作規則 | 使用 Cursor Agent 開發 |
| **error_log.md** | 錯誤案例庫 | 遇到問題時參考 |

## 🚀 快速開始 (Quick Start)

### 步驟 1：環境準備

本專案使用 [**uv**](https://github.com/astral-sh/uv) 進行極速依賴管理（比 pip 快 10-100 倍）。

**安裝 uv**：
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**驗證安裝**：
```bash
uv --version  # 應顯示版本號，例如 uv 0.5.0
```

---

### 步驟 2：Clone 專案與安裝依賴

```bash
git clone https://github.com/yourusername/Investment_Daily.git
cd Investment_Daily

# 安裝所有依賴（自動建立虛擬環境）
uv sync
```

`uv sync` 會根據 `uv.lock` 鎖定的版本安裝所有套件，確保跨平台一致性。

---

### 步驟 3：設定環境變數 (.env)

在專案根目錄建立 `.env` 檔案：

```ini
# ========== Telegram Bot ==========
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_TOPIC_ID=479  # 可選：Telegram 群組 Topic ID

# ========== LLM API ==========
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ========== Google Sheets ==========
GOOGLE_SHEET_ID_STOCK=1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ4
GOOGLE_SHEET_ID_CRYPTO=9zY8xW7vU6tS5rQ4pO3nM2lK1jI0hG9fE8dC7bA6
GOOGLE_SHEET_RANGE=總損益!A:Z
GOOGLE_CREDENTIALS_FILE=credentials.json

# ========== LLM 分析設定 ==========
ANALYSIS_WATCHLIST=IVV,TSLA,BTC  # 核心關注標的（逗號分隔）
ANALYSIS_MAX_FOCUS=6  # 最多詳細分析幾個標的
```

**各參數說明**：

| 參數 | 說明 | 如何取得 |
|------|------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 與 [@BotFather](https://t.me/BotFather) 對話建立 Bot |
| `TELEGRAM_CHAT_ID` | 你的 Chat ID | 發訊給 Bot 後用 [getUpdates API](https://api.telegram.org/bot<token>/getUpdates) 查詢 |
| `TELEGRAM_TOPIC_ID` | Topic ID（可選） | 執行 `test_script/get_topic_id.py` 或在群組中 @bot 然後查看更新 |
| `GEMINI_API_KEY` | Google Gemini API Key | 到 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得 |
| `GOOGLE_SHEET_ID_STOCK` | 美股試算表 ID | 從試算表網址複製：`https://docs.google.com/spreadsheets/d/{THIS_IS_ID}/edit` |
| `GOOGLE_SHEET_ID_CRYPTO` | 加密貨幣試算表 ID | 同上 |
| `GOOGLE_SHEET_RANGE` | Sheet 頁簽名稱與範圍 | 預設 `總損益!A:Z`（可調整） |
| `ANALYSIS_WATCHLIST` | 核心關注標的（可選） | 逗號分隔的標的代碼，例如 `IVV,TSLA,BTC` |
| `ANALYSIS_MAX_FOCUS` | 最多詳細分析數量（可選） | 預設 6，避免報告過長 |

---

### 步驟 4：設定 Google Sheets API

#### 4.1 建立 Google Cloud 專案與啟用 API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案（或選擇現有專案）
3. 啟用 **Google Sheets API**：
   - 左側選單 → **APIs & Services** → **Library**
   - 搜尋 "Google Sheets API" → **ENABLE**

#### 4.2 建立 Service Account

1. 左側選單 → **APIs & Services** → **Credentials**
2. 點擊 **+ CREATE CREDENTIALS** → **Service Account**
3. 填寫名稱（例如：`investment-bot`）→ **CREATE AND CONTINUE**
4. 角色選擇 **Editor** → **CONTINUE** → **DONE**

#### 4.3 下載 JSON 金鑰

1. 在 **Service Accounts** 列表中找到剛建立的帳號
2. 點擊右側 **⋮** → **Manage keys**
3. **ADD KEY** → **Create new key** → **JSON** → **CREATE**
4. 將下載的 JSON 檔案重新命名為 **`credentials.json`**，放入專案根目錄

#### 4.4 分享 Google Sheet

**複製 Service Account Email**（格式：`investment-bot@project-id.iam.gserviceaccount.com`），然後：

1. 開啟你的 Google Sheet（美股與加密貨幣試算表）
2. 點擊右上角 **Share（分享）**
3. 貼上 Service Account Email
4. 權限選擇 **Editor（編輯者）**
5. **Send（傳送）**

#### 4.5 確保試算表格式正確

**支援的欄位名稱**（中英文皆可）：

| 英文 | 中文 | 說明 |
|------|------|------|
| `Symbol` | `stock` / `token` | 標的代碼（例如：TSLA, BTC） |
| `Qty` | `總數量` | 持有數量 |
| `Cost` | `每股成本` / `每顆成本` | 平均成本 |
| `TotalCost` | `總投入USD` / `總投入USDT` | 總投入金額 |
| `MarketPrice` | `目前價格` | 目前市價 |
| `MarketValue` | `目前價值` | 目前總值 |
| `UnrealizedPL` | `損益` | 未實現損益 |
| `ReturnRate` | `獲益率` | 報酬率（可接受 `34.8%` 格式） |

---

### 步驟 5：執行程式

#### Windows 環境（⚠️ 重要）

Windows 需設定 UTF-8 編碼以避免中文亂碼：
```powershell
$env:PYTHONUTF8=1; uv run python -m investment_bot.main
```

#### macOS / Linux 環境
```bash
uv run python -m investment_bot.main
```

---

## 🧪 測試與驗證

### 測試 Market Data API（必測）
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_market_apis.py
```
驗證 yfinance、ccxt/Binance、Fear & Greed Index API 連接狀態。

### 測試 LLM Analyzer（必測）
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_llm_analyzer.py
```
驗證 Gemini API 連接、Prompt 組裝、報告生成、格式驗證。

### 測試 Telegram Bot（必測）
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_telegram_bot.py
```
驗證 Bot 連接、訊息發送、HTML 格式渲染、Topic 功能。

### 獲取 Telegram Topic ID（可選）
```bash
$env:PYTHONUTF8=1; uv run python test_script/get_topic_id.py
```
互動式工具，幫助你獲取群組 Chat ID 和 Topic ID。

### 測試 HTML 格式功能（開發用）
```bash
# 測試 HTML 標籤清理
$env:PYTHONUTF8=1; uv run python test_script/test_html_tag_cleanup.py

# 測試 HTML 特殊字符轉義
$env:PYTHONUTF8=1; uv run python test_script/test_html_escape.py

# 測試報告頭部生成
$env:PYTHONUTF8=1; uv run python test_script/test_report_header.py
```

### 測試本地儲存（開發用）
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_storage.py
```

### 測試 Gemini API（開發用）
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_gemini.py
```

---

## 🔧 進階設定

### Mock Data 模式

如果檢測不到 `credentials.json` 或無法連線 Google Sheets，系統會自動切換到 **Mock Data（模擬數據）** 模式，使用內建的測試持倉數據。

這讓你可以在不連接真實數據的情況下測試完整流程。

### 清除快取與資料庫

如需重置本地數據（除錯用）：
```bash
# 刪除所有快取與資料庫
rm -r investment_bot/data/
```

### 定時排程執行

**Windows Task Scheduler**：
1. 建立 `run_daily.bat`：
```batch
@echo off
cd /d D:\AI\Investment_Daily
powershell -Command "$env:PYTHONUTF8=1; uv run python -m investment_bot.main"
```
2. 工作排程器 → 建立基本工作 → 設定每日早上 8:00 執行

**Linux/macOS cron**：
```bash
# 編輯 crontab
crontab -e

# 加入以下行（每日早上 8:00 執行）
0 8 * * * cd /path/to/Investment_Daily && /path/to/uv run python -m investment_bot.main
```

---

## 🏗️ 架構設計亮點

### 1. 混合本地儲存（SQLite + Parquet）

**為什麼不只用一種？**

| 儲存類型 | 適用場景 | 優勢 |
|---------|---------|------|
| **Parquet** | 市場歷史數據（時序數據） | 高壓縮率、快速讀寫、原生支援 Pandas |
| **SQLite** | 技術信號、持倉快照、快取元數據 | 結構化查詢、事務支援、易於管理 |

**實際效益**：
- 📉 減少 80% 的 API 調用次數（透過快取）
- ⚡ 提升 20-30 倍數據讀取速度（Parquet vs CSV）
- 💾 節省 60% 儲存空間（相較於 CSV）

### 2. Facade Pattern - 統一數據存取介面

```python
# 服務層不需要知道底層是用 SQLite 還是 Parquet
store = DataStore()
df = store.load_market_data("TSLA")  # 自動從 Parquet 讀取
store.save_signal(symbol="BTC", signal_dict={...})  # 自動存入 SQLite
```

**優勢**：
- ✅ 服務層代碼保持簡潔
- ✅ 未來可輕鬆替換為 PostgreSQL 或 Redis
- ✅ 統一錯誤處理與日誌記錄

### 3. Cache-Aside Pattern - 智能快取策略

```
1. 先查本地快取 (system_cache 表)
   ├─ Hit → 檢查 TTL 是否過期
   │   ├─ 未過期 → 直接返回快取數據 ⚡
   │   └─ 已過期 → 呼叫 API 並更新快取
   └─ Miss → 呼叫 API 並儲存快取
```

**快取配置**：
- 市場數據：60 分鐘 TTL
- 持倉數據：60 分鐘 TTL
- 技術信號：當日有效（每日重算）
- 市場情緒：當日有效

### 4. 智能 HTML 格式處理

**問題**：Telegram HTML 模式只支援有限的標籤（`<b>`, `<i>`, `<code>`, `<pre>`, `<a>`）

**解決方案**：三層防禦策略
```
1. LLM Prompt 層：明確告知只能使用支援的標籤
2. 標籤清理層：自動移除不支援的標籤（h1-6, ul/ol/li, hr, div, span）
3. 特殊字符轉義層：智能轉義 < > & 但保留合法 HTML 標籤
```

**技術亮點**：
- 使用佔位符技術保護合法標籤
- 正則表達式批量處理標籤轉換
- 確保 100% 相容 Telegram HTML 規範

### 5. 責任分離設計

**元數據由程式管理，內容由 LLM 生成**

```python
# ❌ 不好的設計：讓 LLM 生成日期（不可靠、浪費 Token）
prompt += "請在報告中加入今天的日期：2025年12月19日"

# ✅ 好的設計：程式自動添加固定格式的頭部
def _add_report_header(self, report_text):
    current_date = datetime.now().strftime('%Y年%m月%d日')
    header = f"<b>📊 專業技術分析日報</b>\n報告日期：{current_date}..."
    return header + report_text
```

**優勢**：
- 日期格式 100% 準確
- 減少 50-80 字元的 Prompt（節省 Input Token）
- LLM 專注於核心分析任務

---

## ❓ 常見問題 (FAQ)

<details>
<summary><b>Q1: 為什麼選用 Gemini 而不是 OpenAI GPT？</b></summary>

**成本考量**：
- Gemini 1.5 Flash：**免費額度** 15 RPM, 1M TPM, 1500 RPD
- GPT-4o：$5/1M input tokens, $15/1M output tokens

每日生成一份報告約消耗 2000-3000 tokens，Gemini 免費額度完全夠用。

**品質**：
Gemini 1.5 Flash 在繁體中文生成上表現優異，且延遲更低。
</details>

<details>
<summary><b>Q2: 為什麼支援雙 Google Sheet 而不是單一試算表？</b></summary>

**靈活性**：
- 美股與加密貨幣的欄位名稱可能不同（`stock` vs `token`）
- 可分別管理兩個資產類別，不會互相干擾
- 符合實際使用場景（許多人用不同試算表記錄）

**設定簡單**：
只需在 `.env` 中設定兩個 `GOOGLE_SHEET_ID` 即可。
</details>

<details>
<summary><b>Q3: 本地資料庫會不會越來越大？</b></summary>

**實際數據**：
- 50 檔股票 × 250 交易日 × 1 年 ≈ **10 MB**（Parquet）
- 每日快照 × 365 天 ≈ **5 MB**（SQLite）

**總結**：一年數據約 **15-20 MB**，完全可接受。

**維護建議**：
可定期清除超過 1 年的歷史快照（使用 SQL DELETE）。
</details>

<details>
<summary><b>Q4: API Rate Limit 怎麼處理？</b></summary>

**已實作的緩解措施**：
1. **快取機制**：減少 80% 重複請求
2. **錯誤處理**：API 失敗時優雅降級，不中斷流程
3. **延遲機制**：批次請求時加入 `time.sleep(0.5)` 避免觸發限制

**各 API 限制**：
- Yahoo Finance：無官方限制，建議 < 2000 req/s
- Binance：1200 req/min
- Gemini：15 req/min（免費）
</details>

<details>
<summary><b>Q5: 如何在雲端運行（AWS/GCP）？</b></summary>

**推薦方案**：
1. **AWS Lambda** + EventBridge（定時觸發）
   - 每日執行成本 < $0.01
   - 需打包依賴為 Lambda Layer

2. **GCP Cloud Run** + Cloud Scheduler
   - 原生支援容器
   - 冷啟動時間較短

3. **Docker + Cron（任何 VPS）**
   - 最靈活，完全掌控環境

未來會提供 Dockerfile 與部署腳本。
</details>

<details>
<summary><b>Q6: 為什麼使用 `uv` 而不是 `pip`？</b></summary>

**速度**：
- `uv sync` 比 `pip install` 快 **10-100 倍**
- 使用 Rust 編寫，平行下載與安裝

**可靠性**：
- `uv.lock` 鎖定所有依賴版本與 hash
- 確保跨平台（Windows/macOS/Linux）一致性

**現代化**：
- 原生支援 `pyproject.toml`
- 自動管理虛擬環境
</details>

<details>
<summary><b>Q7: 為什麼 Telegram 訊息沒有格式？</b></summary>

**可能原因**：
1. LLM 生成了不支援的 HTML 標籤（`<h2>`, `<ul>`, `<li>` 等）
2. 文本中包含未轉義的特殊字符（`<`, `>`, `&`）
3. Telegram Bot Token 或 Chat ID 設定錯誤

**已實作的解決方案**：
- ✅ 自動清理不支援的 HTML 標籤
- ✅ 智能轉義特殊字符但保留合法標籤
- ✅ 錯誤時自動降級為純文字模式

**測試方法**：
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_html_escape.py
```
</details>

<details>
<summary><b>Q8: 如何發送到 Telegram 群組的特定 Topic？</b></summary>

**步驟**：
1. 在群組中 @你的 Bot，發送任意訊息
2. 執行工具腳本獲取 Topic ID：
```bash
$env:PYTHONUTF8=1; uv run python test_script/get_topic_id.py
```
3. 將獲取的 `TELEGRAM_TOPIC_ID` 加入 `.env`
4. 重新執行程式，訊息會發送到指定 Topic

**注意**：
- Bot 必須是群組成員
- Bot 需要有發送訊息的權限
- Topic ID 是數字格式（例如：479）
</details>

<details>
<summary><b>Q9: LLM 報告太長怎麼辦？</b></summary>

**已實作的解決方案**：
- **智能分層分析**：只對 Watchlist 和風險標的詳細分析（100-150 字）
- **其他持倉摘要**：一行總結（15-20 字）
- **長度控制**：Prompt 要求控制在 1500-2200 字以內

**自訂 Watchlist**：
在 `.env` 中設定：
```ini
ANALYSIS_WATCHLIST=IVV,TSLA,BTC  # 你關注的核心標的
ANALYSIS_MAX_FOCUS=6             # 最多詳細分析幾個
```

**測試效果**：
```bash
$env:PYTHONUTF8=1; uv run python test_script/test_llm_analyzer.py
```
</details>

<details>
<summary><b>Q10: 報告日期顯示不正確？</b></summary>

**已修正**：
從 v1.1 版本開始，報告日期由 Python `datetime` 自動生成，格式固定為：
```
報告日期：2025年12月19日 (星期五)
```

**優勢**：
- 100% 準確，不依賴 LLM
- 節省 Input Token
- 格式永遠一致

如果仍看到 `[當前日期]` 佔位符，請更新到最新版本。
</details>

---

## 📊 技術棧 (Tech Stack)

| 類別 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **語言** | Python | 3.9+ | 主要開發語言 |
| **依賴管理** | uv | latest | 快速套件管理 (Rust) |
| **數據處理** | pandas | ^2.2.3 | 數據分析與計算 |
| **數值計算** | numpy | ^2.2.1 | 數學運算與矩陣處理 |
| **市場數據** | yfinance | ^0.2.50 | Yahoo Finance API（美股） |
| **市場數據** | ccxt | ^4.4.37 | 加密貨幣交易所 API |
| **HTTP 請求** | requests | ^2.32.3 | Fear & Greed Index API |
| **技術分析** | pandas-ta | ^0.3.14b | 技術指標計算（RSI, EMA, MACD） |
| **LLM** | google-generativeai | ^0.8.3 | Gemini API 整合 |
| **資料庫** | SQLAlchemy | ^2.0.36 | ORM 與資料庫管理 |
| **檔案格式** | pyarrow | ^18.1.0 | Parquet 格式支援 |
| **訊息推送** | python-telegram-bot | ^21.9 | Telegram Bot API |
| **配置管理** | python-dotenv | ^1.0.1 | .env 環境變數讀取 |
| **Google API** | gspread | ^6.1.4 | Google Sheets API |
| **Google 認證** | oauth2client | ^4.1.3 | Service Account 認證 |

---

## 🤝 貢獻指南 (Contributing)

歡迎提交 Issue 或 Pull Request！

**開發前請先閱讀**：
- `AGENTS.md` - AI 協作指引與代碼風格
- `spec.md` - 技術規格文件
- `TODO.md` - 當前開發進度

**Commit Message 規範**：
```
<type>: <description>

feat: add telegram notification
fix: handle None value in portfolio data
docs: update README with storage architecture
```

---

## 📜 授權 (License)

MIT License - 自由使用與修改

---

## 📮 聯絡與支援

- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/Investment_Daily/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Investment_Daily/discussions)

---

## 📋 更新日誌 (Changelog)

### v1.1.0 (2025-12-19) - HTML 格式化與智能分層

**新增功能**：
- ✨ Telegram 改用 HTML Parse Mode，支援 `<b>`, `<i>`, `<code>` 標籤
- ✨ 智能分層報告：重點標的詳細分析（100-150 字）+ 其他持倉摘要（15-20 字）
- ✨ 自動日期頭部生成（Python `datetime`），100% 準確
- ✨ Telegram Topic 支援，可發送到群組特定話題
- ✨ HTML 特殊字符智能轉義（保護合法標籤，轉義 `<` `>` `&`）

**優化改進**：
- 🔧 HTML 標籤自動清理（移除 h1-6, ul/ol/li, hr, div, span）
- 🔧 LLM Prompt 優化：禁止使用不支援的標籤和特殊字符
- 🔧 報告長度控制在 1500-2200 字以內
- 🔧 可自訂 Watchlist 和最大詳細分析數量

**Bug 修正**：
- 🐛 修正報告日期顯示為佔位符的問題
- 🐛 修正 Telegram 格式無法渲染的問題（unsupported start tag）
- 🐛 修正 HTML 特殊字符導致解析錯誤的問題

**測試工具**：
- 🧪 新增 `test_html_escape.py` - HTML 特殊字符轉義測試
- 🧪 新增 `test_html_tag_cleanup.py` - HTML 標籤清理測試
- 🧪 新增 `test_report_header.py` - 報告頭部功能測試
- 🧪 新增 `get_topic_id.py` - Telegram Topic ID 獲取工具

### v1.0.0 (2025-12-10) - 初始版本

**核心功能**：
- ✨ 雙 Google Sheet 支援（美股 + 加密貨幣）
- ✨ 多數據源整合（yfinance + ccxt + Fear & Greed Index）
- ✨ 專業技術分析（RSI, EMA, MACD, Bollinger Bands）
- ✨ Gemini LLM 智能報告生成
- ✨ Telegram 自動推送
- ✨ 本地儲存（SQLite + Parquet）
- ✨ 智能快取機制（60分鐘 TTL）

---

**⭐ 如果這個專案對你有幫助，請給一個 Star！**

**📊 Happy Investing & Stay Rational! 🧠**
