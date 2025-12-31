# -*- coding: utf-8 -*-
"""
測試 Skip List 邏輯
驗證 LLMAnalyzerService 是否正確忽略 ANALYSIS_SKIP_LIST 中的標的
"""

import sys
from pathlib import Path

# 加入專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from investment_bot.services.llm_analyzer import LLMAnalyzerService
from investment_bot.config import Config

def test_skip_list_selection():
    """測試篩選邏輯是否包含黑名單過濾"""
    print("=" * 80)
    print("  測試 LLMAnalyzerService 的 Skip List 篩選邏輯")
    print("=" * 80)
    print()
    
    # 初始化服務
    service = LLMAnalyzerService()
    
    # 建立測試數據
    portfolio_summary = {"assets": []} # 篩選邏輯不依賴 assets
    
    # 建立技術信號，包含一個在 skip list 中的標的
    tech_signals = {
        "TSLA": {"rsi": 45, "trend": "Bullish"}, # 正常標的
        "BTC": {"rsi": 80, "is_overbought": True, "trend": "Bullish"}, # 風險標的
        "IB01.L": {"rsi": 50, "trend": "Bullish"} # 黑名單標的
    }
    
    # 設定測試用的 Config (手動覆蓋)
    Config.ANALYSIS_WATCHLIST = ["TSLA"]
    Config.ANALYSIS_SKIP_LIST = ["IB01.L", "BTC"] # 把 BTC 也加進去測試
    
    print(f"🔧 測試設定:")
    print(f"  - Watchlist: {Config.ANALYSIS_WATCHLIST}")
    print(f"  - Skip List: {Config.ANALYSIS_SKIP_LIST}")
    print(f"  - 所有標的: {list(tech_signals.keys())}")
    print()
    
    # 執行篩選
    print("🔨 執行 _select_focus_symbols...")
    focus, summary = service._select_focus_symbols(portfolio_summary, tech_signals)
    
    print()
    print(f"📊 篩選結果:")
    print(f"  - 重點標的 (Focus): {focus}")
    print(f"  - 摘要標的 (Summary): {summary}")
    print()
    
    # 驗證
    all_passed = True
    
    # 1. 黑名單不應出現在任何清單中
    for skip_symbol in Config.ANALYSIS_SKIP_LIST:
        if skip_symbol in focus or skip_symbol in summary:
            print(f"  ❌ 錯誤: {skip_symbol} 應該被跳過，但出現在結果中")
            all_passed = False
        else:
            print(f"  ✅ 成功: {skip_symbol} 已被正確跳過")
            
    # 2. Watchlist 中的 TSLA 應在 focus 中
    if "TSLA" in focus:
        print(f"  ✅ 成功: TSLA 正確出現在 Focus 中")
    else:
        print(f"  ❌ 錯誤: TSLA 應該在 Focus 中")
        all_passed = False
        
    print()
    if all_passed:
        print("=" * 80)
        print("  ✅ 篩選邏輯測試通過！")
        print("=" * 80)
    else:
        print("=" * 80)
        print("  ❌ 篩選邏輯測試失敗")
        print("=" * 80)
        
    return all_passed

if __name__ == "__main__":
    test_skip_list_selection()
