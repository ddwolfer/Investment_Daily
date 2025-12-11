# -*- coding: utf-8 -*-
"""
本地儲存與快取整合測試 (Local Storage Integration Test)
驗證 Market Data (Parquet) 與 Tech Signals (SQLite) 的快取機制。
"""

import sys
import os
import pandas as pd
import time
from datetime import datetime

# Ensure investment_bot can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_storage_integration():
    print("🚀 Starting Storage Integration Test...\n")

    try:
        from investment_bot.utils.data_store import DataStore
        from investment_bot.services.market_data import MarketDataService
        from investment_bot.services.tech_analysis import TechnicalAnalysisService
        from investment_bot.services.google_sheet import GoogleSheetService
        
        store = DataStore()
        
        # --- 1. Market Data Cache Test ---
        print('=== 1. Market Data Cache Test ===')
        market = MarketDataService()
        symbol = 'TSLA'
        
        # Force clear cache for test
        print(f"  Clearing cache for {symbol}...")
        parquet_path = store.get_market_data_path(symbol)
        if os.path.exists(parquet_path):
            os.remove(parquet_path)
        # Clear system cache key
        with store.db.get_connection() as conn:
            from sqlalchemy import text
            conn.execute(text(f"DELETE FROM system_cache WHERE key = 'market_data_{symbol}'"))
            conn.commit()
            
        print("  [Step 1] First Fetch (Should hit API)...")
        start_time = time.time()
        df1 = market.get_historical_data(symbol, 'Stock')
        duration1 = time.time() - start_time
        print(f"  Rows: {len(df1)}, Time: {duration1:.4f}s")
        
        print("  [Step 2] Second Fetch (Should hit Cache)...")
        start_time = time.time()
        df2 = market.get_historical_data(symbol, 'Stock')
        duration2 = time.time() - start_time
        print(f"  Rows: {len(df2)}, Time: {duration2:.4f}s")
        
        if duration2 < duration1 and not df2.empty:
            print("  ✅ Cache Speedup Verified!")
        else:
            print("  ⚠️ Cache might not be working as expected (or API was very fast).")

        # --- 2. Tech Signal Storage Test ---
        print('\n=== 2. Tech Signal Storage Test ===')
        ta = TechnicalAnalysisService()
        
        if not df1.empty:
            print("  Analyzing and Saving Signals...")
            signals = ta.analyze(df1, 'Stock', symbol=symbol)
            
            # Verify DB content
            last_date = df1.index[-1].strftime('%Y-%m-%d')
            saved_signal = store.get_signal(symbol, last_date)
            
            if saved_signal:
                print(f"  ✅ Signal Retrieved from DB for {last_date}")
                print(f"  RSI: {saved_signal['rsi']}")
            else:
                print("  ❌ Signal not found in DB!")
        
        # --- 3. Portfolio Snapshot Test ---
        print('\n=== 3. Portfolio Snapshot Test ===')
        
        # Clear portfolio cache to ensure fresh fetch
        print("  Clearing portfolio cache...")
        with store.db.get_connection() as conn:
            from sqlalchemy import text
            conn.execute(text("DELETE FROM system_cache WHERE key = 'portfolio_data'"))
            conn.commit()
        
        sheet = GoogleSheetService()
        
        print(f"  [Test] Service connected: {sheet.service is not None}")
        print(f"  [Test] Stock Sheet ID configured: {sheet.stock_sheet_id is not None}")
        print(f"  [Test] Crypto Sheet ID configured: {sheet.crypto_sheet_id is not None}")

        # This will fetch from Google Sheet API (or Mock if failed)
        portfolio = sheet.get_portfolio_data()

        # Display the fetched data
        if not portfolio.empty:
            print("\n  [Portfolio Data Content]")
            # 顯示標準化的欄位名稱（程式內部使用的）
            display_cols = ['Symbol', 'Qty', 'Cost', 'MarketPrice', 'UnrealizedPL', 'ReturnRate', 'Type']
            available_cols = [col for col in display_cols if col in portfolio.columns]
            if available_cols:
                print(portfolio[available_cols].to_string())
            else:
                # 如果標準欄位不存在，顯示所有欄位
                print(portfolio.to_string())
        
        # Verify DB
        today = datetime.now().strftime('%Y-%m-%d')
        with store.db.get_connection() as conn:
            from sqlalchemy import text
            result = conn.execute(text(f"SELECT COUNT(*) FROM portfolio_snapshots WHERE date = '{today}'")).scalar()
            print(f"  ✅ Portfolio Snapshots in DB for {today}: {result}")
            
    except Exception as e:
        print(f"  ❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nTest Complete.")

if __name__ == "__main__":
    test_storage_integration()

