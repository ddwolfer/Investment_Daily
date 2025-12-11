# -*- coding: utf-8 -*-
"""
數據存儲介面 (Data Store Facade)
統一處理 Service 與底層儲存 (SQLite/Parquet) 的互動。
實現快取優先策略。
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select, insert, update
from .db_manager import DBManager

class DataStore:
    def __init__(self):
        self.db = DBManager()
        self.market_data_dir = "investment_bot/data/market_data"
        os.makedirs(self.market_data_dir, exist_ok=True)
        
    # --- Market Data (Parquet) ---
    
    def get_market_data_path(self, symbol):
        """取得 Parquet 檔案路徑"""
        # 簡單處理 symbol 中的特殊字符 (如 BTC/USDT -> BTC_USDT)
        safe_symbol = symbol.replace('/', '_')
        return os.path.join(self.market_data_dir, f"{safe_symbol}.parquet")

    def save_market_data(self, df, symbol):
        """
        儲存 K 線數據到 Parquet
        採 Overwrite 策略：簡單起見，直接覆蓋舊檔 (因為我們每次都抓完整的 200+ 天)
        """
        if df.empty:
            return
        path = self.get_market_data_path(symbol)
        df.to_parquet(path)
        
        # 更新快取記錄 (標記今日已更新)
        self.set_cache(f"market_data_{symbol}", "updated", ttl_minutes=60*12) # 12小時快取

    def load_market_data(self, symbol):
        """從 Parquet 讀取 K 線數據"""
        path = self.get_market_data_path(symbol)
        if os.path.exists(path):
            try:
                # 讀取 Parquet
                df = pd.read_parquet(path)
                
                # 檢查是否為「今日已更新」
                # 雖然檔案存在，但可能是昨天的。我們檢查 cache key
                if self.get_cache(f"market_data_{symbol}"):
                    return df
                
                # 如果 cache 過期，我們還是回傳 df，讓 Service 層決定是否要透過 API 更新
                # 這裡可以設計成回傳 (df, is_stale)
                return df
                
            except Exception as e:
                print(f"讀取 Parquet 失敗 {symbol}: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def is_market_data_fresh(self, symbol):
        """檢查數據是否新鮮 (Cache Key 是否存在)"""
        return self.get_cache(f"market_data_{symbol}") is not None

    # --- Tech Signals (SQLite) ---
    
    def save_signal(self, symbol, asset_type, date_str, signal_dict):
        """儲存技術分析結果"""
        # 準備寫入資料
        values = {
            'symbol': symbol,
            'asset_type': asset_type,
            'date': date_str,
            'current_price': signal_dict.get('current_price'),
            'rsi': signal_dict.get('rsi'),
            'is_overbought': signal_dict.get('is_overbought'),
            'is_oversold': signal_dict.get('is_oversold'),
            'trend': signal_dict.get('trend'),
            'ema_fast': signal_dict['ema_values'].get('fast'),
            'ema_mid': signal_dict['ema_values'].get('mid'),
            'ema_slow': signal_dict['ema_values'].get('slow'),
            'macd_line': signal_dict['macd'].get('line'),
            'macd_signal': signal_dict['macd'].get('signal'),
            'macd_hist': signal_dict['macd'].get('hist'),
            'bb_upper': signal_dict['bb'].get('upper'),
            'bb_lower': signal_dict['bb'].get('lower'),
            'bb_pct_b': signal_dict['bb'].get('pct_b')
        }
        
        with self.db.get_connection() as conn:
            # 使用 Upsert (Insert or Replace)
            # SQLite 的 INSERT OR REPLACE 語法，但在 SQLAlchemy 中我們可以用 delete + insert 簡單處理
            # 或者先查詢是否存在
            table = self.db.tech_signals
            
            # 刪除舊的 (如果有)
            conn.execute(
                table.delete().where(
                    (table.c.symbol == symbol) & (table.c.date == date_str)
                )
            )
            # 插入新的
            conn.execute(table.insert().values(**values))
            conn.commit()

    def get_signal(self, symbol, date_str):
        """查詢特定日期的信號"""
        table = self.db.tech_signals
        with self.db.get_connection() as conn:
            result = conn.execute(
                select(table).where(
                    (table.c.symbol == symbol) & (table.c.date == date_str)
                )
            ).first()
            
            if result:
                # 轉回 dict (類似 tech_analysis Service 的輸出格式)
                row = result._mapping
                return {
                    "current_price": row['current_price'],
                    "rsi": row['rsi'],
                    "is_overbought": row['is_overbought'],
                    "is_oversold": row['is_oversold'],
                    "trend": row['trend'],
                    "ema_values": {
                        "fast": row['ema_fast'],
                        "mid": row['ema_mid'],
                        "slow": row['ema_slow']
                    },
                    "macd": {
                        "line": row['macd_line'],
                        "signal": row['macd_signal'],
                        "hist": row['macd_hist']
                    },
                    "bb": {
                        "upper": row['bb_upper'],
                        "lower": row['bb_lower'],
                        "pct_b": row['bb_pct_b']
                    }
                }
        return None

    # --- Portfolio Snapshots (SQLite) ---
    
    def save_portfolio_snapshot(self, df, date_str):
        """儲存持倉快照"""
        if df.empty:
            return
            
        table = self.db.portfolio_snapshots
        
        with self.db.get_connection() as conn:
            # 1. 清除當日舊快照 (避免重複)
            conn.execute(table.delete().where(table.c.date == date_str))
            
            # 2. 批量插入
            values_list = []
            for _, row in df.iterrows():
                values_list.append({
                    'date': date_str,
                    'symbol': row['Symbol'],
                    'asset_type': row['Type'],
                    'qty': row['Qty'],
                    'cost_basis': row['Cost'],
                    'market_price': row['MarketPrice'],
                    'market_value': row['MarketPrice'] * row['Qty'],
                    'unrealized_pl': row['UnrealizedPL'],
                    'return_rate': row['ReturnRate']
                })
            
            if values_list:
                conn.execute(table.insert(), values_list)
                conn.commit()

    # --- Market Sentiment (SQLite) ---
    
    def save_sentiment(self, date_str, sentiment_data):
        table = self.db.market_sentiment
        with self.db.get_connection() as conn:
            # Delete old
            conn.execute(table.delete().where(table.c.date == date_str))
            # Insert new
            conn.execute(table.insert().values(
                date=date_str,
                value=sentiment_data['value'],
                classification=sentiment_data['classification']
            ))
            conn.commit()

    def get_sentiment(self, date_str):
        table = self.db.market_sentiment
        with self.db.get_connection() as conn:
            result = conn.execute(
                select(table).where(table.c.date == date_str)
            ).first()
            if result:
                return {
                    "value": result.value,
                    "classification": result.classification
                }
        return None

    # --- Cache Management ---
    
    def set_cache(self, key, value, ttl_minutes=60):
        """設定快取"""
        expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
        table = self.db.system_cache
        
        with self.db.get_connection() as conn:
            # Delete old
            conn.execute(table.delete().where(table.c.key == key))
            # Insert
            conn.execute(table.insert().values(
                key=key,
                value=json.dumps(value),
                expires_at=expires_at
            ))
            conn.commit()
            
    def get_cache(self, key):
        """取得快取 (若過期則回傳 None)"""
        table = self.db.system_cache
        now = datetime.now()
        
        with self.db.get_connection() as conn:
            result = conn.execute(
                select(table).where(
                    (table.c.key == key) & (table.c.expires_at > now)
                )
            ).first()
            
            if result:
                return json.loads(result.value)
        return None

