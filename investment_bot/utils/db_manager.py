# -*- coding: utf-8 -*-
"""
資料庫管理員 (Database Manager)
負責 SQLite 資料庫的連線、初始化與 Schema 管理。
使用 SQLAlchemy Core 進行操作，保持輕量高效。
"""

import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func

class DBManager:
    def __init__(self, db_path="investment_bot/data/investment.db"):
        # 確保目錄存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 使用 SQLite
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.metadata = MetaData()
        
        # 定義 Schema
        self._define_tables()
        
        # 建立 Tables (如果不存在)
        self.metadata.create_all(self.engine)
        
    def _define_tables(self):
        """定義資料庫表結構"""
        
        # 1. 技術信號表 (Tech Signals)
        self.tech_signals = Table('tech_signals', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('symbol', String, nullable=False),
            Column('asset_type', String, nullable=False),
            Column('date', String, nullable=False), # SQLite 不直接支援 Date，存 ISO 格式字串 'YYYY-MM-DD'
            
            # 價格
            Column('current_price', Float),
            
            # RSI
            Column('rsi', Float),
            Column('is_overbought', Boolean),
            Column('is_oversold', Boolean),
            
            # Trend
            Column('trend', String),
            Column('ema_fast', Float),
            Column('ema_mid', Float),
            Column('ema_slow', Float),
            
            # MACD
            Column('macd_line', Float),
            Column('macd_signal', Float),
            Column('macd_hist', Float),
            
            # Bollinger Bands
            Column('bb_upper', Float),
            Column('bb_lower', Float),
            Column('bb_pct_b', Float),
            
            Column('created_at', DateTime, server_default=func.now()),
            UniqueConstraint('symbol', 'date', name='uix_signal_symbol_date')
        )
        
        # 2. 持倉快照表 (Portfolio Snapshots)
        self.portfolio_snapshots = Table('portfolio_snapshots', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('date', String, nullable=False),
            Column('symbol', String, nullable=False),
            Column('asset_type', String, nullable=False),
            
            Column('qty', Float),
            Column('cost_basis', Float),
            Column('market_price', Float),
            Column('market_value', Float),
            Column('unrealized_pl', Float),
            Column('return_rate', Float),
            
            Column('created_at', DateTime, server_default=func.now())
        )
        # 手動建立 Index 需使用 Index 物件 (Table 定義外)
        Index('idx_portfolio_date', self.portfolio_snapshots.c.date)
        
        # 3. 市場情緒表 (Market Sentiment)
        self.market_sentiment = Table('market_sentiment', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('date', String, nullable=False, unique=True),
            Column('value', Integer),
            Column('classification', String),
            Column('created_at', DateTime, server_default=func.now())
        )
        
        # 4. 系統快取表 (System Cache)
        self.system_cache = Table('system_cache', self.metadata,
            Column('key', String, primary_key=True),
            Column('value', String), # JSON string
            Column('expires_at', DateTime),
            Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
        )
        
    def get_connection(self):
        return self.engine.connect()

