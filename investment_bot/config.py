# -*- coding: utf-8 -*-
"""
設定模組 (Configuration Module)
負責管理所有的參數設定、Ticker 映射以及技術指標的閾值。
"""
import os
from dotenv import load_dotenv

# 強制指定 .env 路徑在專案根目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 往上一層
env_path = os.path.join(project_root, '.env')

# 只在 .env 檔案存在時才載入（避免在 GitHub Actions 等環境中產生警告）
# 在 GitHub Actions 中，環境變數會直接透過 Secrets 設定，不需要 .env 檔案
if os.path.exists(env_path):
    load_dotenv(env_path)

class Config:
    # --- API Keys ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_TOPIC_ID = os.getenv("TELEGRAM_TOPIC_ID")  # 群組 Topic ID (可選)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    # 雙 Google Sheet 支援（美股 + 加密貨幣）
    GOOGLE_SHEET_ID_STOCK = os.getenv("GOOGLE_SHEET_ID_STOCK")
    GOOGLE_SHEET_ID_CRYPTO = os.getenv("GOOGLE_SHEET_ID_CRYPTO")
    GOOGLE_SHEET_RANGE = os.getenv("GOOGLE_SHEET_RANGE", "總損益!A:Z")  # 預設頁簽名稱
    
    # 向下兼容：如果只設定了舊的 GOOGLE_SHEET_ID，則作為 Stock Sheet 使用
    if not GOOGLE_SHEET_ID_STOCK and os.getenv("GOOGLE_SHEET_ID"):
        GOOGLE_SHEET_ID_STOCK = os.getenv("GOOGLE_SHEET_ID")

    # --- Ticker Mapping (將 Sheet 中的名稱映射到 API 所需的 Symbol) ---
    # Crypto: 使用 Binance 格式 (e.g., BTC/USDT)
    # 注意：這裡需要根據使用者的實際 Google Sheet 內容進行擴充
    CRYPTO_MAPPING = {
        "BTC": "BTC/USDT",
        "ETH": "ETH/USDT",
        "SOL": "SOL/USDT",
        "BNB": "BNB/USDT",
        "WLD": "WLD/USDT",
    }
    
    # Stock: 使用 Yahoo Finance 格式
    STOCK_MAPPING = {
        "TSLA": "TSLA",
        "NVDA": "NVDA",
        "IVV": "IVV",
        "AAPL": "AAPL",
        "MSFT": "MSFT",
        "COIN": "COIN",
    }

    # --- 技術指標參數 (Technical Analysis Parameters) ---
    
    # RSI 週期
    RSI_PERIOD_STOCK = 14  # 美股標準
    RSI_PERIOD_CRYPTO = 6  # 加密貨幣 (更敏感)
    
    # RSI 閾值 (Thresholds)
    RSI_OVERBOUGHT = 75
    RSI_OVERSOLD = 30
    
    # EMA 週期 (美股趨勢)
    EMA_SHORT = 20
    EMA_MEDIUM = 60
    EMA_LONG = 120
    
    # Crypto 短線 EMA
    EMA_CRYPTO_FAST = 5
    EMA_CRYPTO_MID = 10
    EMA_CRYPTO_SLOW = 20

    # MACD 參數
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    # Bollinger Bands
    BB_WINDOW = 20
    BB_STD_DEV = 2

    # --- LLM 設定 (Gemini API) ---
    GEMINI_MODEL = "gemini-flash-latest"
    GEMINI_MAX_RETRIES = 3
    GEMINI_TEMPERATURE = 0.7  # 創意度（0-1）
    GEMINI_MAX_OUTPUT_TOKENS = 15000  # 最大輸出長度
    
    # --- LLM 分析設定 ---
    # Watchlist: 始終進行詳細分析的標的（核心關注）
    ANALYSIS_WATCHLIST = ["IVV", "TSLA", "BTC"]
    
    # 跳過分析的標的（例如：現金儲備類資產、超短期美債）
    # 這些標的不會進行技術分析，也不會出現在詳細報告中
    ANALYSIS_SKIP_LIST = ["IB01.L"]
    
    # 最多詳細分析的標的數量（避免 token 超標）
    ANALYSIS_MAX_FOCUS = 6
    
    # 最小市值佔比閾值（例如 0.01 = 1%）
    # 市值佔比低於此值的標的，不會出現在詳細分析或簡要總結中
    # 但 Watchlist 和風險警示標的不受此限制（即使佔比很小也會分析）
    ANALYSIS_MIN_PERCENTAGE = 0.01  # 1%

