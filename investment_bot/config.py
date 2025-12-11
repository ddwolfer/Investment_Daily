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

# 載入
load_dotenv(env_path)

class Config:
    # --- API Keys ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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

