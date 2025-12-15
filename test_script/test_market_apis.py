# -*- coding: utf-8 -*-
"""
Market Data API 整合測試
測試項目：
1. yfinance API（美股）
2. ccxt/Binance API（加密貨幣）
3. Fear & Greed Index API
4. 快取機制驗證
5. 錯誤處理測試
"""

import sys
import time
from datetime import datetime
sys.path.insert(0, '.')

from investment_bot.services.market_data import MarketDataService
from investment_bot.utils.data_store import DataStore

def print_separator(title=""):
    """印出分隔線"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('-'*60)

def test_stock_data():
    """測試 yfinance API（美股）"""
    print_separator("[1/5] 測試 yfinance API (美股)")
    
    service = MarketDataService()
    test_symbols = [
        ('TSLA', 'Stock', '特斯拉'),
        ('NVDA', 'Stock', '輝達'),
        ('IVV', 'Stock', 'S&P 500 ETF')
    ]
    
    results = []
    for symbol, asset_type, name in test_symbols:
        try:
            print(f"\n  測試 {symbol} ({name})...")
            df = service.get_historical_data(symbol, asset_type, days=200)
            
            if not df.empty:
                latest_price = df['Close'].iloc[-1]
                data_count = len(df)
                latest_date = df.index[-1].strftime('%Y-%m-%d')
                
                print(f"    ✅ 成功: {data_count} 筆數據")
                print(f"       最新價格: ${latest_price:.2f}")
                print(f"       最新日期: {latest_date}")
                
                # 驗證數據完整性
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    print(f"    ⚠️  缺少欄位: {missing_cols}")
                else:
                    print(f"    ✅ 欄位完整: {required_cols}")
                
                results.append({
                    'symbol': symbol,
                    'success': True,
                    'count': data_count,
                    'price': latest_price
                })
            else:
                print(f"    ❌ 失敗: 無數據返回")
                results.append({'symbol': symbol, 'success': False})
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
            results.append({'symbol': symbol, 'success': False, 'error': str(e)})
    
    # 總結
    success_count = sum(1 for r in results if r.get('success'))
    print(f"\n  總結: {success_count}/{len(test_symbols)} 個測試通過")
    return results

def test_crypto_data():
    """測試 ccxt/Binance API（加密貨幣）"""
    print_separator("[2/5] 測試 ccxt/Binance API (加密貨幣)")
    
    service = MarketDataService()
    test_symbols = [
        ('BTC', 'Crypto', '比特幣'),
        ('ETH', 'Crypto', '以太坊'),
        ('SOL', 'Crypto', 'Solana')
    ]
    
    results = []
    for symbol, asset_type, name in test_symbols:
        try:
            print(f"\n  測試 {symbol} ({name})...")
            df = service.get_historical_data(symbol, asset_type, days=200)
            
            if not df.empty:
                latest_price = df['Close'].iloc[-1]
                data_count = len(df)
                latest_date = df.index[-1].strftime('%Y-%m-%d')
                
                print(f"    ✅ 成功: {data_count} 筆數據")
                print(f"       最新價格: ${latest_price:,.2f}")
                print(f"       最新日期: {latest_date}")
                
                # 驗證數據格式
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    print(f"    ⚠️  缺少欄位: {missing_cols}")
                else:
                    print(f"    ✅ 欄位完整: {required_cols}")
                
                results.append({
                    'symbol': symbol,
                    'success': True,
                    'count': data_count,
                    'price': latest_price
                })
            else:
                print(f"    ❌ 失敗: 無數據返回")
                results.append({'symbol': symbol, 'success': False})
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
            results.append({'symbol': symbol, 'success': False, 'error': str(e)})
    
    # 總結
    success_count = sum(1 for r in results if r.get('success'))
    print(f"\n  總結: {success_count}/{len(test_symbols)} 個測試通過")
    return results

def test_fear_greed_index():
    """測試 Fear & Greed Index API"""
    print_separator("[3/5] 測試 Fear & Greed Index API")
    
    service = MarketDataService()
    
    try:
        print("\n  獲取市場情緒指數...")
        sentiment = service.get_market_sentiment()
        
        if sentiment and 'value' in sentiment:
            value = sentiment['value']
            classification = sentiment['classification']
            
            print(f"    ✅ 成功")
            print(f"       指數值: {value}")
            print(f"       分類: {classification}")
            
            # 驗證數據合理性
            if 0 <= value <= 100:
                print(f"    ✅ 數值範圍正確 (0-100)")
            else:
                print(f"    ⚠️  數值範圍異常: {value}")
            
            return {'success': True, 'value': value, 'classification': classification}
        else:
            print(f"    ❌ 失敗: 回傳格式異常")
            return {'success': False}
            
    except Exception as e:
        print(f"    ❌ 錯誤: {e}")
        return {'success': False, 'error': str(e)}

def test_cache_mechanism():
    """測試快取機制"""
    print_separator("[4/5] 測試快取機制")
    
    service = MarketDataService()
    test_symbol = 'TSLA'
    
    print(f"\n  測試標的: {test_symbol}")
    
    # 第一次調用（應該從 API 抓取或使用舊快取）
    print("\n  第一次調用（檢查快取狀態）...")
    start_time = time.time()
    df1 = service.get_historical_data(test_symbol, 'Stock', days=200)
    time1 = time.time() - start_time
    
    if not df1.empty:
        print(f"    ✅ 成功: {len(df1)} 筆數據")
        print(f"       耗時: {time1:.3f} 秒")
    else:
        print(f"    ❌ 失敗: 無數據返回")
        return {'success': False}
    
    # 第二次調用（應該命中快取）
    print("\n  第二次調用（應該命中快取）...")
    start_time = time.time()
    df2 = service.get_historical_data(test_symbol, 'Stock', days=200)
    time2 = time.time() - start_time
    
    if not df2.empty:
        print(f"    ✅ 成功: {len(df2)} 筆數據")
        print(f"       耗時: {time2:.3f} 秒")
        
        # 計算速度提升
        if time2 > 0:
            speedup = time1 / time2
            print(f"\n  📊 快取效能分析:")
            print(f"     第一次: {time1:.3f} 秒")
            print(f"     第二次: {time2:.3f} 秒")
            print(f"     速度提升: {speedup:.1f}x")
            
            if speedup > 5:
                print(f"    ✅ 快取機制運作正常（速度提升 > 5x）")
            else:
                print(f"    ⚠️  快取效果不明顯（可能快取已存在）")
        
        return {
            'success': True,
            'time1': time1,
            'time2': time2,
            'speedup': speedup if time2 > 0 else 0
        }
    else:
        print(f"    ❌ 失敗: 第二次調用無數據")
        return {'success': False}

def test_error_handling():
    """測試錯誤處理"""
    print_separator("[5/5] 測試錯誤處理")
    
    service = MarketDataService()
    
    # 測試無效的美股 Symbol
    print("\n  測試無效美股 Symbol: INVALID_STOCK")
    df1 = service.get_historical_data('INVALID_STOCK', 'Stock', days=200)
    
    if df1.empty:
        print(f"    ✅ 正確處理: 返回空 DataFrame")
    else:
        print(f"    ⚠️  非預期: 返回了 {len(df1)} 筆數據")
    
    # 測試無效的加密貨幣 Symbol
    print("\n  測試無效加密貨幣 Symbol: FAKECOIN")
    df2 = service.get_historical_data('FAKECOIN', 'Crypto', days=200)
    
    if df2.empty:
        print(f"    ✅ 正確處理: 返回空 DataFrame")
    else:
        print(f"    ⚠️  非預期: 返回了 {len(df2)} 筆數據")
    
    # 總結
    print("\n  總結:")
    if df1.empty and df2.empty:
        print(f"    ✅ 錯誤處理機制正常（Graceful Degradation）")
        return {'success': True}
    else:
        print(f"    ⚠️  錯誤處理需要改進")
        return {'success': False}

def main():
    """主測試流程"""
    print("=" * 60)
    print("  Market Data API 整合測試")
    print("  測試時間:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    all_results = {}
    
    # 執行測試
    try:
        all_results['stock'] = test_stock_data()
        all_results['crypto'] = test_crypto_data()
        all_results['sentiment'] = test_fear_greed_index()
        all_results['cache'] = test_cache_mechanism()
        all_results['error_handling'] = test_error_handling()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被使用者中斷")
        return
    except Exception as e:
        print(f"\n\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 最終總結
    print_separator("測試總結")
    
    print("\n  📊 測試結果:")
    
    # 美股測試
    stock_success = sum(1 for r in all_results.get('stock', []) if r.get('success'))
    stock_total = len(all_results.get('stock', []))
    print(f"    ✅ 美股 API: {stock_success}/{stock_total} 通過")
    
    # 加密貨幣測試
    crypto_success = sum(1 for r in all_results.get('crypto', []) if r.get('success'))
    crypto_total = len(all_results.get('crypto', []))
    print(f"    ✅ 加密貨幣 API: {crypto_success}/{crypto_total} 通過")
    
    # 情緒指數測試
    sentiment_ok = all_results.get('sentiment', {}).get('success', False)
    print(f"    {'✅' if sentiment_ok else '❌'} Fear & Greed Index: {'通過' if sentiment_ok else '失敗'}")
    
    # 快取測試
    cache_ok = all_results.get('cache', {}).get('success', False)
    cache_speedup = all_results.get('cache', {}).get('speedup', 0)
    print(f"    {'✅' if cache_ok else '❌'} 快取機制: {'通過' if cache_ok else '失敗'}", end='')
    if cache_ok and cache_speedup > 0:
        print(f" (速度提升 {cache_speedup:.1f}x)")
    else:
        print()
    
    # 錯誤處理測試
    error_ok = all_results.get('error_handling', {}).get('success', False)
    print(f"    {'✅' if error_ok else '❌'} 錯誤處理: {'通過' if error_ok else '失敗'}")
    
    # 計算總成功率
    total_tests = stock_total + crypto_total + 3  # +3 for sentiment, cache, error_handling
    total_success = stock_success + crypto_success + (1 if sentiment_ok else 0) + (1 if cache_ok else 0) + (1 if error_ok else 0)
    
    print(f"\n  📈 總體通過率: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("  測試完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

