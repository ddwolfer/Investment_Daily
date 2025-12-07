# -*- coding: utf-8 -*-
"""
市場數據服務 (Market Data Service)
負責從 Yahoo Finance 與 Binance (via ccxt) 獲取實時行情與歷史 K 線數據。
"""

import yfinance as yf
import ccxt
import pandas as pd
import requests
from datetime import datetime, timedelta
from ..config import Config

class MarketDataService:
    def __init__(self):
        """初始化市場數據服務"""
        self.exchange = ccxt.binance()
        # 如果有 API Key 可以設置，但讀取公開行情通常不需要
        # self.exchange.apiKey = '...' 
        
    def get_historical_data(self, symbol, asset_type, days=200):
        """
        獲取歷史 K 線數據 (OHLCV)
        :param symbol: 標的代碼 (e.g., 'TSLA' or 'BTC')
        :param asset_type: 'Stock' or 'Crypto'
        :param days: 抓取天數
        :return: DataFrame with index as Date, columns: Open, High, Low, Close, Volume
        """
        try:
            if asset_type == 'Crypto':
                return self._get_crypto_history(symbol, days)
            else:
                # 預設為 Stock
                return self._get_stock_history(symbol, days)
        except Exception as e:
            print(f"獲取數據失敗 {symbol}: {e}")
            return pd.DataFrame()

    def _get_stock_history(self, symbol, days):
        """使用 yfinance 獲取美股歷史數據"""
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
        # 轉換 Symbol: Config.CRYPTO_MAPPING 已經是 API 格式 (BTC/USDT)
        mapped_symbol = Config.CRYPTO_MAPPING.get(symbol, f"{symbol}/USDT")
        
        # 計算 timeframe
        timeframe = '1d'
        # ccxt limit 限制通常是 500 or 1000
        limit = min(days + 100, 1000) 
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(mapped_symbol, timeframe, limit=limit)
        except Exception as e:
            print(f"CCXT fetch error for {mapped_symbol}: {e}")
            return pd.DataFrame()
        
        if not ohlcv:
            return pd.DataFrame()

        # 轉為 DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('Date', inplace=True)
        df.drop(columns=['timestamp'], inplace=True)
        
        return df

    def get_fear_and_greed_index(self):
        """
        獲取恐懼與貪婪指數
        這裡使用 alternative.me API (Crypto)
        """
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            data = response.json()
            value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            return {"value": value, "classification": classification}
        except Exception as e:
            print(f"獲取恐懼貪婪指數失敗: {e}")
            return {"value": 50, "classification": "Neutral"}

