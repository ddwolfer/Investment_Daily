# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd

# Ensure investment_bot can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_services():
    print("Starting Integrated Service Test...")

    # --- 1. Test Market Data ---
    print('=== 1. Testing Market Data ===')
    df_stock = pd.DataFrame()
    try:
        from investment_bot.services.market_data import MarketDataService
        market = MarketDataService()
        
        print("  Testing Stock (TSLA)...")
        df_stock = market.get_historical_data('TSLA', 'Stock')
        print(f"  TSLA Data Rows: {len(df_stock)}")
        if not df_stock.empty: 
            print(f"  Sample: {df_stock.index[-1].date()} Close: {df_stock['Close'].iloc[-1]:.2f}")
            
        print("  Testing Crypto (BTC)...")
        df_crypto = market.get_historical_data('BTC', 'Crypto')
        print(f"  BTC Data Rows: {len(df_crypto)}")
        
    except Exception as e:
        print(f"  Market Data Failed: {e}")
        import traceback
        traceback.print_exc()

    # --- 2. Test Technical Analysis ---
    print('\n=== 2. Testing Technical Analysis ===')
    try:
        from investment_bot.services.tech_analysis import TechnicalAnalysisService
        ta = TechnicalAnalysisService()
        
        if not df_stock.empty:
            print("  Analyzing TSLA data...")
            signals = ta.analyze(df_stock, 'Stock')
            print(f"  Signals: {signals}")
        else:
            print("  Skipping TA test (No stock data available)")
            
    except Exception as e:
        print(f"  TA Failed: {e}")
        import traceback
        traceback.print_exc()

    # --- 3. Test Google Sheet ---
    print('\n=== 3. Testing Google Sheet ===')
    try:
        from investment_bot.services.google_sheet import GoogleSheetService
        sheet = GoogleSheetService()
        
        # Check if Mock Data is used
        if not sheet.service:
            print("  Google API not connected, using Mock Data mode.")
            
        portfolio = sheet.get_portfolio_data()
        print(f"  Portfolio Rows: {len(portfolio)}")
        if not portfolio.empty:
            print(portfolio[['Symbol', 'Qty', 'Cost', 'UnrealizedPL']].head(3).to_string())
        else:
            print("  Portfolio is empty.")
            
    except Exception as e:
        print(f"  Sheet Failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nTest Complete.")

if __name__ == "__main__":
    test_services()

