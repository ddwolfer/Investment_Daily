# System Architecture Design: Local Data Storage & Caching
# (系統架構設計：本地數據儲存與快取)

## 1. 設計目標 (Design Goals)
為了減少對外部 API (Yahoo Finance, Binance, Google Sheets) 的依賴，降低被限流的風險，並建立可回溯的歷史數據庫，本系統將導入 **混合式本地儲存 (Hybrid Local Storage)** 架構。

### 核心原則
1.  **快取優先 (Cache First)**：所有數據請求先查本地，過期或不存在才請求 API。
2.  **歷史留存 (History Retention)**：不只是快取，更要記錄每天的分析結果與持倉變化，以利未來回測與趨勢分析。
3.  **輕量高效 (Lightweight & Efficient)**：使用 Python 內建的 SQLite 處理關聯數據，Parquet 處理大量 K 線數據。

## 2. 儲存架構 (Storage Architecture)

### 2.1 混合儲存策略
我們將數據分為兩類，採用不同的儲存方式：

| 數據類型 | 儲存方式 | 原因 | 更新頻率 |
| :--- | :--- | :--- | :--- |
| **歷史 K 線 (OHLCV)** | **Parquet 檔案** | 數據量大、結構固定、主要用於批量讀取。 | 每日追加 (Append) |
| **技術分析結果** | **SQLite 資料庫** | 需關聯查詢、按日期比較、數據量適中。 | 每日新增 |
| **持倉快照** | **SQLite 資料庫** | 需追蹤資產變化、計算歷史損益。 | 每日新增 |
| **市場情緒** | **SQLite 資料庫** | 單點數據，適合時間序列存儲。 | 每日新增 |
| **快取元數據** | **SQLite 資料庫** | 管理過期時間 (TTL)。 | 每次讀寫 |

### 2.2 目錄結構
```
investment_bot/
├── data/
│   ├── investment.db          # SQLite (分析結果、持倉、情緒、快取管理)
│   └── market_data/           # Parquet (K 線數據)
│       ├── stock/
│       │   └── TSLA.parquet
│       └── crypto/
│           └── BTC.parquet
├── utils/
│   ├── db_manager.py          # SQLite 連線與 Schema 管理
│   └── data_store.py          # 統一數據存取介面 (Facade Pattern)
```

## 3. 資料庫 Schema 設計 (SQLite)

### 3.1 技術信號表 (`tech_signals`)
記錄每天每個標的的技術指標狀態，用於生成日報與長期趨勢分析。

```sql
CREATE TABLE tech_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,      -- 'Stock' or 'Crypto'
    date DATE NOT NULL,
    
    -- 價格資訊
    current_price REAL,
    
    -- RSI
    rsi REAL,
    is_overbought BOOLEAN,
    is_oversold BOOLEAN,
    
    -- Trend (EMA)
    trend TEXT,                    -- 'Bullish' or 'Bearish'
    ema_fast REAL,
    ema_mid REAL,
    ema_slow REAL,
    
    -- MACD
    macd_line REAL,
    macd_signal REAL,
    macd_hist REAL,
    
    -- Bollinger Bands
    bb_upper REAL,
    bb_lower REAL,
    bb_pct_b REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)           -- 確保每天每標的只有一筆記錄
);
```

### 3.2 持倉快照表 (`portfolio_snapshots`)
記錄每天的持倉狀態，用於計算整體淨值曲線 (Equity Curve)。

```sql
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    
    qty REAL,
    cost_basis REAL,               -- 平均成本
    market_price REAL,             -- 當下市價
    market_value REAL,             -- 市值 (Qty * Price)
    unrealized_pl REAL,            -- 未實現損益
    return_rate REAL,              -- 報酬率
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_portfolio_date ON portfolio_snapshots(date);
```

### 3.3 市場情緒表 (`market_sentiment`)
```sql
CREATE TABLE market_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    value INTEGER,                 -- 0-100
    classification TEXT,           -- 'Extreme Fear', 'Greed', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 系統快取表 (`system_cache`)
用於管理 API 請求的冷卻時間。

```sql
CREATE TABLE system_cache (
    key TEXT PRIMARY KEY,          -- e.g., 'market_data_update_TSLA'
    value TEXT,                    -- JSON payload (optional)
    expires_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 模組職責更新 (Module Updates)

### 4.1 `utils/data_store.py` (New)
這是所有 Service 與底層儲存的溝通橋樑。
*   `save_market_data(df, symbol)`: 將 K 線存入 Parquet。
*   `load_market_data(symbol)`: 讀取 Parquet。
*   `save_signal(signal_dict)`: 寫入 SQLite `tech_signals`。
*   `get_latest_signal(symbol)`: 查詢最新信號。
*   `save_portfolio_snapshot(df)`: 寫入 SQLite `portfolio_snapshots`。

### 4.2 `services/market_data.py` (Updated)
*   邏輯變更：`get_historical_data`
    1.  檢查 `system_cache` 確認是否今日已更新。
    2.  若已更新 -> 直接讀取 Parquet。
    3.  若未更新 -> 呼叫 API (Yahoo/Binance) -> 更新 Parquet (Append/Overwrite) -> 更新 `system_cache`。

### 4.3 `services/tech_analysis.py` (Updated)
*   邏輯變更：`analyze`
    1.  計算完指標後，呼叫 `data_store.save_signal` 存入 DB。
    2.  如果 DB 中已有今日數據，可選擇直接回傳（避免重複計算）。

### 4.4 `services/google_sheet.py` (Updated)
*   邏輯變更：`get_portfolio_data`
    1.  檢查快取 (TTL: 1小時)。
    2.  若過期 -> 呼叫 Google Sheet API -> 存入 DB 快照 -> 更新快取。

## 5. 數據流 (Data Flow)

1.  **Init**: App 啟動，初始化 SQLite DB (如果不存在)。
2.  **Step 1 (Portfolio)**: 
    *   Check Cache -> (Miss) -> Google API -> Save to DB (`portfolio_snapshots`) & Update Cache.
3.  **Step 2 (Market Data)**:
    *   For each symbol:
        *   Check Cache (Today updated?) -> (No) -> Yahoo/Binance API -> Save to Parquet.
        *   Load Parquet to DataFrame.
4.  **Step 3 (Analysis)**:
    *   Compute TA -> Save to DB (`tech_signals`).
5.  **Step 4 (Reporting)**:
    *   LLM Service 讀取 DataFrame 與 DB 中的歷史上下文 (例如：昨天 RSI 是多少 vs 今天)。
    *   Generate Report.

## 6. 未來擴展性 (Future Proofing)
*   **回測系統 (Backtesting)**: 有了 Parquet (價格) 與 SQLite (信號)，可以直接寫腳本回測策略勝率。
*   **Web Dashboard**: SQLite 可以直接作為 Streamlit 或 Flask 的後端，展示資產曲線圖。

