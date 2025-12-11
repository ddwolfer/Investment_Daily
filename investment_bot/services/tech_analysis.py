# -*- coding: utf-8 -*-
"""
技術分析服務 (Technical Analysis Service)
負責計算 RSI, EMA, MACD, Bollinger Bands 等技術指標。
整合 DataStore 儲存分析結果。
"""

import pandas as pd
import ta
from datetime import datetime
from ..config import Config
from ..utils.data_store import DataStore

class TechnicalAnalysisService:
    def __init__(self):
        self.store = DataStore()

    def analyze(self, df, asset_type, symbol=None):
        """
        對傳入的 DataFrame 進行技術分析
        :param df: 包含 Open, High, Low, Close, Volume 的 DataFrame
        :param asset_type: 'Stock' or 'Crypto'
        :param symbol: (Optional) 用於儲存結果到 DB，若無提供則不儲存
        :return: 包含指標的字典
        """
        # 檢查數據量是否足夠
        if df.empty or len(df) < 20:
            return None

        # 如果有提供 symbol，先檢查今日是否已分析過
        if symbol:
            today = datetime.now().strftime('%Y-%m-%d')
            # 因為 K 線可能不是每天都有 (週末休市)，我們用 DataFrame 的最新日期作為 Key
            # 但為了每日報告，通常還是希望能看到當下的分析狀態
            # 這裡我們用「最新數據日期」來查詢是否已分析
            last_date_str = df.index[-1].strftime('%Y-%m-%d')
            
            cached_signal = self.store.get_signal(symbol, last_date_str)
            if cached_signal:
                # print(f"  [TA Cache Hit] {symbol} {last_date_str}")
                return cached_signal

        try:
            # 取得 Close 價格序列
            close = df['Close']
            
            # 1. RSI
            rsi_period = Config.RSI_PERIOD_CRYPTO if asset_type == 'Crypto' else Config.RSI_PERIOD_STOCK
            rsi_indicator = ta.momentum.RSIIndicator(close=close, window=rsi_period)
            current_rsi = rsi_indicator.rsi().iloc[-1]
            
            # 2. EMA
            # 確保數據長度足夠計算 EMA
            data_len = len(close)
            
            if asset_type == 'Crypto':
                ema_fast_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_FAST).ema_indicator().iloc[-1]
                ema_mid_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_MID).ema_indicator().iloc[-1]
                ema_slow_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_SLOW).ema_indicator().iloc[-1]
                # 對於 Crypto，我們用 EMA 60 作為趨勢分界線 (如果數據夠長)
                if data_len >= 60:
                    ema_trend_val = ta.trend.EMAIndicator(close=close, window=60).ema_indicator().iloc[-1]
                else:
                    ema_trend_val = ema_slow_val
            else:
                # 美股
                ema_fast_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_SHORT).ema_indicator().iloc[-1]
                
                if data_len >= Config.EMA_MEDIUM:
                    ema_mid_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_MEDIUM).ema_indicator().iloc[-1]
                    ema_trend_val = ema_mid_val
                else:
                    ema_mid_val = ema_fast_val
                    ema_trend_val = ema_fast_val
                    
                if data_len >= Config.EMA_LONG:
                    ema_slow_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_LONG).ema_indicator().iloc[-1]
                else:
                    ema_slow_val = ema_mid_val
                
            # 3. MACD
            macd = ta.trend.MACD(close=close, window_slow=Config.MACD_SLOW, window_fast=Config.MACD_FAST, window_sign=Config.MACD_SIGNAL)
            macd_line = macd.macd().iloc[-1]
            macd_signal = macd.macd_signal().iloc[-1]
            macd_hist = macd.macd_diff().iloc[-1]
            
            # 4. Bollinger Bands (布林帶)
            bb = ta.volatility.BollingerBands(close=close, window=Config.BB_WINDOW, window_dev=Config.BB_STD_DEV)
            bb_upper = bb.bollinger_hband().iloc[-1]
            bb_lower = bb.bollinger_lband().iloc[-1]
            
            # 當前價格
            current_price = close.iloc[-1]
            
            # 組裝訊號
            signals = {
                "current_price": round(current_price, 2),
                "rsi": round(current_rsi, 2),
                "is_overbought": current_rsi > Config.RSI_OVERBOUGHT,
                "is_oversold": current_rsi < Config.RSI_OVERSOLD,
                "trend": "Bullish" if current_price > ema_trend_val else "Bearish",
                "ema_values": {
                    "fast": round(ema_fast_val, 2),
                    "mid": round(ema_mid_val, 2),
                    "slow": round(ema_slow_val, 2)
                },
                "macd": {
                    "line": round(macd_line, 2),
                    "signal": round(macd_signal, 2),
                    "hist": round(macd_hist, 2)
                },
                "bb": {
                    "upper": round(bb_upper, 2),
                    "lower": round(bb_lower, 2),
                    "pct_b": round((current_price - bb_lower) / (bb_upper - bb_lower), 2) if (bb_upper - bb_lower) != 0 else 0
                }
            }
            
            # 儲存結果到 DB (如果有 symbol)
            if symbol:
                last_date_str = df.index[-1].strftime('%Y-%m-%d')
                self.store.save_signal(symbol, asset_type, last_date_str, signals)
            
            return signals
        except Exception as e:
            print(f"技術分析計算錯誤 {symbol}: {e}")
            return None
