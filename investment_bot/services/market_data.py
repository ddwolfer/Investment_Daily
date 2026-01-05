# -*- coding: utf-8 -*-
"""
市場數據服務 (Market Data Service)
負責從 Yahoo Finance 與 CoinGecko API 獲取實時行情與歷史 K 線數據。
整合 DataStore 實現快取優先策略。

注意：已改用 CoinGecko API 替代 Binance，避免 GitHub Actions 地區限制問題。
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from ..config import Config
from ..utils.data_store import DataStore

class MarketDataService:
    def __init__(self):
        """初始化市場數據服務"""
        self.store = DataStore()
        # 不再使用 ccxt.binance()，改用 CoinGecko API
        
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
        """
        使用 CoinGecko API 獲取加密貨幣歷史數據（替代 Binance，避免地區限制）
        
        CoinGecko API 優點：
        - 無地區限制（適合 GitHub Actions）
        - 免費額度充足（50 calls/minute）
        - API 穩定可靠
        """
        # CoinGecko 的 symbol 映射（CoinGecko 使用 coin ID 而非 symbol）
        coingecko_id_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "WLD": "worldcoin-wld",
            "LINK": "chainlink",
            "BGB": "bitget-token",
            # 可以根據需要擴充更多映射
        }
        
        coingecko_id = coingecko_id_map.get(symbol)
        
        if not coingecko_id:
            # 如果找不到映射，嘗試使用 symbol 的小寫（CoinGecko 可能支援）
            coingecko_id = symbol.lower()
            print(f"  [MarketData] 警告: {symbol} 未在 CoinGecko 映射表中，嘗試使用 {coingecko_id}")
        
        try:
            # CoinGecko API: 獲取歷史價格數據
            # 文檔：https://www.coingecko.com/api/documentations/v3
            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": min(days, 365),  # CoinGecko 免費版最多 365 天
                "interval": "daily"
            }
            
            print(f"  [MarketData] 正在從 CoinGecko 獲取 {symbol} 數據...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 解析價格數據
            prices = data.get('prices', [])
            if not prices:
                print(f"  [MarketData] 警告: CoinGecko 未返回 {symbol} 的價格數據")
                return pd.DataFrame()
            
            # 轉換為 DataFrame
            df = pd.DataFrame(prices, columns=['Timestamp', 'Close'])
            df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
            df.set_index('Date', inplace=True)
            
            # CoinGecko 的 market_chart 只提供價格，不提供完整的 OHLCV
            # 為了技術分析需要，我們使用 Close 價格作為 Open, High, Low（簡化處理）
            # 這對於 EMA, RSI, MACD 等指標計算影響不大
            df['Open'] = df['Close']
            df['High'] = df['Close']
            df['Low'] = df['Close']
            df['Volume'] = 0  # CoinGecko market_chart 不提供 Volume
            
            # 重新排列欄位順序（符合標準 OHLCV 格式）
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.drop(columns=['Timestamp'], inplace=True, errors='ignore')
            
            # 確保數據按日期排序（從舊到新）
            df = df.sort_index()
            
            print(f"  [MarketData] ✅ 成功獲取 {symbol} 數據 ({len(df)} 筆)")
            return df
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  [MarketData] ❌ CoinGecko 找不到 {symbol} (ID: {coingecko_id})，請檢查映射表")
            else:
                print(f"  [MarketData] ❌ CoinGecko API 錯誤 ({e.response.status_code}): {e}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            print(f"  [MarketData] ❌ CoinGecko 網路錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"  [MarketData] ❌ CoinGecko 下載錯誤 {symbol}: {e}")
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
