# Project Specification: AI Investment Daily Report Bot (AI 投資日報機器人)

## 1. 專案概述 (Project Overview)

本專案旨在建立一個自動化的 Python 投資分析系統。
目標： 每天早上從 Google Sheets 讀取投資組合，獲取市場實時行情與歷史數據，進行技術指標計算 (Technical Analysis)，並透過 LLM (如 OpenAI/Gemini/Claude) 生成一份具備「風控官」思維的投資日報，最後發送至 Telegram。

**核心人設 (Persona)**： 
理性數據派的風控官 (Rational Risk Manager)。
風格： 數據優先、保護利潤、客觀分析風險。

## 2. 檔案結構 (Project Structure)

請依照以下結構建立檔案：
```
investment_bot/
├── .env                    # 存放 API Keys (Google, Telegram, OpenAI/Anthropic)
├── requirements.txt        # Python 依賴庫
├── config.py               # 設定檔 (Ticker Mapping, 閾值設定)
├── main.py                 # 主程式入口
├── services/
│   ├── google_sheet.py     # 讀取 Google Sheet 持倉數據
│   ├── market_data.py      # yfinance & ccxt 抓取價格與歷史數據
│   ├── tech_analysis.py    # 計算 RSI, MACD, EMA, BB 等指標
│   ├── llm_analyzer.py     # 構建 Prompt 並呼叫 LLM 生成報告
│   └── telegram_bot.py     # 發送 Markdown 訊息
└── utils/
    └── formatters.py       # 數字格式化與 Emoji 處理工具
```

## 3. 環境與依賴 (Prerequisites)

`.env` 變數需求
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_key  # 或 ANTHROPIC_API_KEY / GEMINI_API_KEY
GOOGLE_CREDENTIALS_FILE=credentials.json # Google Service Account Key
GOOGLE_SHEET_ID=your_sheet_id
```

`requirements.txt` 核心庫
```
pandas
numpy
yfinance
ccxt
ta              # Technical Analysis Library
python-telegram-bot
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
openai          # 或 anthropic / google-generativeai
python-dotenv
```

## 4. 模組詳細規格 (Module Specifications)

### 4.1 配置模組 (`config.py`)

* 定義美股與 Crypto 的 Ticker 映射 (因為 Sheet 裡的名稱可能簡寫)。
* 定義技術指標參數 (RSI 週期, EMA 週期)。
* 關鍵映射 (Ticker Mapping):
    * Crypto: `BTC` -> `BTC/USDT`, `SOL` -> `SOL/USDT`
    * Stock: `TSLA` -> `TSLA`, `IVV` -> `IVV`

### 4.2 數據源模組 (`services/google_sheet.py`)

* 功能： 連接 Google Sheets API。
* 輸入： Sheet ID 與 Range。
* 邏輯：
    * 讀取兩個區塊：美股區塊 (TSLA, IVV...) 與 Crypto 區塊 (BTC, BNB...)。
    * 將數據轉換為 Pandas DataFrame。
    * 欄位標準化： 確保欄位名稱統一為 `Symbol`, `Qty`, `Cost`, `MarketPrice`, `UnrealizedPL`, `ReturnRate`。

### 4.3 市場數據與技術分析 (`services/market_data.py` & `services/tech_analysis.py`)

這是本系統的數學核心。

* 數據抓取 (`market_data.py`):
    * 美股: 使用 `yfinance` 抓取過去 200 天的 OHLCV。
    * Crypto: 使用 `ccxt` (Binance) 抓取過去 200 天的 OHLCV (Timeframe: 1d)。
    * 市場情緒: 抓取 Fear & Greed Index (使用簡單 API 或爬蟲)。
* 技術指標計算 (tech_analysis.py):
    * 使用 `ta` library 針對每個標的計算：
        1. RSI (Relative Strength Index): 週期 6 (敏感/Crypto) 和 14 (標準/美股)。
        2. EMA (Exponential Moving Average): 20, 60, 120。
        3. MACD: Fast=12, Slow=26, Signal=9。
        4. Bollinger Bands: 判斷價格是否觸及上軌/下軌。
    * 信號標記 (Signal Flags):
        1. `is_overbought`: RSI > 75
        2. `is_oversold`: RSI < 30
        3. `trend`: 判斷當前價格是否在 EMA 60 之上 (Bullish/Bearish)。

### 4.4 LLM 分析核心 (services/llm_analyzer.py)

這是系統的「大腦」。

* Input Data Construction: 將上述步驟整理好的 DataFrame 轉為 JSON 格式，包含：
    * Portfolio Summary (總資產、各標的佔比、損益)。
    * Technical Signals (每個標的的 RSI, MACD 狀態)。
    * Market Sentiment (恐慌指數)。

* System Prompt (請在程式碼中使用此 Prompt):
```
Role: You are a professional Investment Risk Manager ("The Rational Data-Driven Advisor").
Objective: Analyze the user's daily portfolio and technical data to generate a concise, actionable Telegram report.

Tone: Professional, calm, objective, data-first. Avoid FOMO.

Format Structure (Markdown):
1. 💼 **Portfolio Snapshot**: Total value, top winners/losers (24h), cash/asset ratio.
2. 📈 **Market & Technical Pulse**: 
   - Sentiment Score (Fear & Greed).
   - Key Technical Signals: Highlight only significant signals (e.g., RSI > 75, Price crossing EMA). 
   - Specifically analyze BTC, TSLA, and NVDA.
3. 🌍 **Macro & News Context**: Briefly interpret how current macro events (Interest rates, CPI) affect this specific portfolio.
4. ⚠️ **Risk Radar**: Highlight concentrated risks (e.g., "Tech sector exposure > 40%").
5. 🎯 **Actionable Advice**:
   - If Asset is Overbought (RSI > 75): Suggest "Trim/Take Profit".
   - If Asset is Oversold (RSI < 30) AND Trend is Up: Suggest "Buy the Dip".
   - For "Free" assets (BNB, SOL): Suggest holding or staking unless structure breaks.

Language: Traditional Chinese (繁體中文).
Output: Clean Markdown, structured for mobile reading.
```

### 4.5 Telegram 通知 (`services/telegram_bot.py`)

* 功能：將生成的 Markdown 文本發送到指定的 Chat ID。
* 細節：需處理 Markdown 特殊字符轉義，避免發送失敗。

### 5. 執行流程 (Execution Flow in `main.py`)

1. Init: 載入 `.env` 設定。
2. Fetch Portfolio: 從 Google Sheets 抓取最新持倉。
3. Fetch Market Data: 根據持倉代碼，抓取歷史 K 線。
4. Compute TA: 計算所有標的的技術指標。
5. Generate Report: 將數據打包餵給 LLM，生成日報文字。
6. Send: 透過 Telegram Bot 發送。
7. Log: 輸出一行簡易 Log 表示執行成功。