# -*- coding: utf-8 -*-
"""
設定模組 (Configuration Module)
負責管理所有的參數設定、Ticker 映射以及技術指標的閾值。
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    # --- API Keys ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

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

