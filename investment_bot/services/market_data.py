# -*- coding: utf-8 -*-
"""
市場數據服務 (Market Data Service)
負責從 Yahoo Finance 與 Binance (via ccxt) 獲取實時行情與歷史 K 線數據。
整合 DataStore 實現快取優先策略。
"""

import yfinance as yf
import ccxt
import pandas as pd
import requests
from datetime import datetime, timedelta
from ..config import Config
from ..utils.data_store import DataStore

class MarketDataService:
    def __init__(self):
        """初始化市場數據服務"""
        self.exchange = ccxt.binance()
        self.store = DataStore()
        
    def get_historical_data(self, symbol, asset_type, days=200):
        """
        獲取歷史 K 線數據 (OHLCV)
        Logic: Check Cache -> (Miss/Stale) -> Fetch API -> Save Cache -> Return
        """
        # 1. Check if data is fresh (cache key exists for today)
        if self.store.is_market_data_fresh(symbol):
            # print(f"  [Cache Hit] {symbol}")
            return self.store.load_market_data(symbol)
            
        # print(f"  [Cache Miss] Fetching API for {symbol}...")
        
        # 2. Fetch from API
        df = pd.DataFrame()
        try:
            if asset_type == 'Crypto':
                df = self._get_crypto_history(symbol, days)
            else:
                df = self._get_stock_history(symbol, days)
        except Exception as e:
            print(f"獲取數據失敗 {symbol}: {e}")
            
        # 3. Save to Store (if valid)
        if not df.empty:
            self.store.save_market_data(df, symbol)
            
        return df

    def _get_stock_history(self, symbol, days):
        
        # 對映 Symbol
        ticker = Config.STOCK_MAPPING.get(symbol, symbol)
        
        # 為了確保有足夠數據計算指標 (如 EMA120)，多抓一點 buffer
        start_date = datetime.now() - timedelta(days=days + 100)
        
        # auto_adjust=True 會讓 Close 變成 Adj Close，適合長期回測
        try:
            df = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
        except Exception as e:
            print(f"yfinance 下載錯誤 {ticker}: {e}")
            return pd.DataFrame()
        
        if df.empty:
            print(f"警告: {ticker} 下載不到數據")
            return df
            
        # yfinance 可能回傳 MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
             df.columns = df.columns.droplevel(1) # 簡單處理，假設只有一個 ticker
        
        return df

    def _get_crypto_history(self, symbol, days):
        """使用 ccxt 獲取加密貨幣歷史數據"""
        # Mapping: BTC -> BTC/USDT
        pair = Config.CRYPTO_MAPPING.get(symbol, f"{symbol}/USDT")
        
        try:
            # fetch_ohlcv (symbol, timeframe, since, limit)
            # 每日線 '1d'
            # limit 預設 500, 我們需要 200 + buffer
            ohlcv = self.exchange.fetch_ohlcv(pair, '1d', limit=days + 100)
            
            # 轉換為 DataFrame
            df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
            df.set_index('Date', inplace=True)
            df.drop(columns=['Timestamp'], inplace=True)
            
            return df
            
        except Exception as e:
            print(f"ccxt 下載錯誤 {pair}: {e}")
            return pd.DataFrame()

    def get_market_sentiment(self):
        """
        獲取恐懼與貪婪指數 (Fear & Greed Index)
        Logic: Check Cache (Today) -> API -> Save
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Check DB Cache
        cached = self.store.get_sentiment(today)
        if cached:
            # print("  [Sentiment Cache Hit]")
            return cached
            
        # 2. Fetch API
        try:
            # Crypto Fear & Greed API
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            
            result = {"value": value, "classification": classification}
            
            # 3. Save to DB
            self.store.save_sentiment(today, result)
            return result
            
        except Exception as e:
            print(f"無法獲取市場情緒: {e}")
            return {"value": 50, "classification": "Neutral"}
