# -*- coding: utf-8 -*-
"""
?銵?????(Technical Analysis Service)
鞎痊閮? RSI, EMA, MACD, Bollinger Bands 蝑?銵?璅?
"""

import pandas as pd
import ta
from ..config import Config

class TechnicalAnalysisService:
    def analyze(self, df, asset_type):
        """
        撠?亦? DataFrame ?脰??銵???
        :param df: ? Open, High, Low, Close, Volume ??DataFrame
        :param asset_type: 'Stock' or 'Crypto'
        :return: ???????
        """
        # 瑼Ｘ?豢???西雲憭?
        if df.empty or len(df) < 20:
            return None

        try:
            # ?? Close ?寞摨?
            close = df['Close']
            
            # 1. RSI
            rsi_period = Config.RSI_PERIOD_CRYPTO if asset_type == 'Crypto' else Config.RSI_PERIOD_STOCK
            rsi_indicator = ta.momentum.RSIIndicator(close=close, window=rsi_period)
            current_rsi = rsi_indicator.rsi().iloc[-1]
            
            # 2. EMA
            # 蝣箔??豢??瑕漲頞喳?閮? EMA
            data_len = len(close)
            
            if asset_type == 'Crypto':
                ema_fast_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_FAST).ema_indicator().iloc[-1]
                ema_mid_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_MID).ema_indicator().iloc[-1]
                ema_slow_val = ta.trend.EMAIndicator(close=close, window=Config.EMA_CRYPTO_SLOW).ema_indicator().iloc[-1]
                # 撠 Crypto嚗???閮?銝銝?60?亦?雿銝剝?隅?Ｗ???(憒??雲憭??
                if data_len >= 60:
                    ema_trend_val = ta.trend.EMAIndicator(close=close, window=60).ema_indicator().iloc[-1]
                else:
                    ema_trend_val = ema_slow_val
            else:
                # 蝢
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
            
            # 4. Bollinger Bands (撣?撣?
            bb = ta.volatility.BollingerBands(close=close, window=Config.BB_WINDOW, window_dev=Config.BB_STD_DEV)
            bb_upper = bb.bollinger_hband().iloc[-1]
            bb_lower = bb.bollinger_lband().iloc[-1]
            
            # ?嗅??寞
            current_price = close.iloc[-1]
            
            # 靽∟??斗
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
            
            return signals
        except Exception as e:
            print(f"?銵???蝞隤? {e}")
            return None

