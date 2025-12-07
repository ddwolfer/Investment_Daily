# AI 投資日報機器人 (AI Investment Daily Bot)

這是一個基於 Python 的自動化投資分析工具，專為同時投資「美股 (US Stocks)」與「加密貨幣 (Crypto)」的投資者設計。

它扮演一位「**理性數據派的風控官 (Rational Risk Manager)**」，每天早上自動分析你的投資組合，計算技術指標 (RSI, EMA, MACD)，並透過 AI 生成一份客觀、拒絕 FOMO 的投資日報，最後發送到 Telegram。

## 核心功能 (Features)

*   **自動化數據串接**：從 Google Sheets 讀取持倉，並自動串接 Yahoo Finance (美股) 與 Binance (Crypto) 獲取實時行情。
*   **專業技術分析**：
    *   **美股**：使用 Trend-following 策略 (EMA 20/60/120, RSI 14)。
    *   **Crypto**：使用高波動策略 (EMA 5/10/20, RSI 6)。
    *   監控 MACD 背離與布林帶 (Bollinger Bands)。
*   **AI 智能報告**：使用 LLM (Gemini 1.5 Flash / Pro) 生成 Markdown 格式日報，包含：
    *   資產概覽與現金水位。
    *   市場情緒 (恐懼與貪婪指數)。
    *   風險提示 (集中度風險、過熱訊號)。
    *   具體的 Actionable Advice (止盈/抄底建議)。
*   **Telegram 推送**：格式優美的 Markdown 訊息直接推送到手機。

## 專案結構 (Project Structure)

```text
investment_bot/
├── .env                    # 設定檔 (API Keys) - 需自行建立
├── config.py               # 參數設定 (Ticker Mapping, 技術指標參數)
├── main.py                 # 主程式入口
├── services/               # 核心服務模組
└── utils/                  # 工具函式
pyproject.toml              # 專案依賴管理 (uv)
README.md                   # 說明文件
```

## 安裝與設定 (Setup)

### 1. 環境準備
本專案推薦使用 [uv](https://github.com/astral-sh/uv) 進行極速安裝與管理。

如果你還沒安裝 `uv`：
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安裝依賴
在專案根目錄下執行：

```bash
uv sync
```
這會自動建立虛擬環境並安裝所有依賴。

### 3. 設定環境變數 (.env)
在專案根目錄下建立 `.env` 檔案，填入以下資訊：

```ini
TELEGRAM_BOT_TOKEN=你的_Telegram_Bot_Token
TELEGRAM_CHAT_ID=你的_Chat_ID
# OPENAI_API_KEY=你的_OpenAI_API_Key  <-- 已棄用
GEMINI_API_KEY=你的_Gemini_API_Key
GOOGLE_SHEET_ID=你的_Google_Sheet_ID
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 4. Google Sheets 設定
1.  到 Google Cloud Console 建立 Service Account，並下載 JSON 金鑰，重新命名為 `credentials.json` 放入專案根目錄。
2.  將你的 Google Sheet 分享給該 Service Account 的 Email 地址 (Editor 權限)。
3.  確保 Sheet 包含以下欄位 (至少)：
    *   `Symbol` (e.g., BTC, TSLA)
    *   `Qty` (持有數量)
    *   `Cost` (平均成本)

### 5. 執行程式

使用 `uv run` 可以直接在虛擬環境中執行，無需手動 activate：

```bash
uv run python -m investment_bot.main
```

## 測試模式 (Test Mode)
如果系統檢測不到 `credentials.json` 或無法連線 Google Sheets，會自動切換到 **Mock Data (模擬數據)** 模式，方便你在不連接真實數據的情況下測試流程。

## 授權 (License)
MIT License
