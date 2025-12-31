# -*- coding: utf-8 -*-
"""
測試市值佔比過濾功能
驗證低於最小佔比的標的是否被正確過濾
"""

import sys
from pathlib import Path

# 加入專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from investment_bot.services.llm_analyzer import LLMAnalyzerService
from investment_bot.config import Config

def test_min_percentage_filter():
    """測試市值佔比過濾邏輯"""
    print("=" * 80)
    print("  測試市值佔比過濾功能")
    print("=" * 80)
    print()
    
    # 初始化服務
    service = LLMAnalyzerService()
    
    # 設定測試用的配置
    Config.ANALYSIS_WATCHLIST = ["TSLA", "BTC"]
    Config.ANALYSIS_SKIP_LIST = ["IB01.L"]
    Config.ANALYSIS_MIN_PERCENTAGE = 0.01  # 1%
    
    # 建立測試數據：總資產 200,000 USD
    total_value = 200000.0
    
    portfolio_summary = {
        "total_value": total_value,
        "assets": [
            {
                "symbol": "TSLA",
                "market_value": 50000.0,  # 25% - 應該被分析（Watchlist）
            },
            {
                "symbol": "BTC",
                "market_value": 80000.0,  # 40% - 應該被分析（Watchlist）
            },
            {
                "symbol": "NVDA",
                "market_value": 30000.0,  # 15% - 應該被分析（> 1%）
            },
            {
                "symbol": "WLD",
                "market_value": 80.0,  # 0.04% - 應該被過濾（< 1%）
            },
            {
                "symbol": "SOL",
                "market_value": 150.0,  # 0.075% - 應該被過濾（< 1%）
            },
            {
                "symbol": "ETH",
                "market_value": 2500.0,  # 1.25% - 應該被分析（> 1%）
            },
            {
                "symbol": "IB01.L",
                "market_value": 10000.0,  # 5% - 應該被跳過（Skip List）
            },
        ]
    }
    
    # 建立技術信號（所有標的都有）
    tech_signals = {
        "TSLA": {"rsi": 50, "trend": "Bullish"},
        "BTC": {"rsi": 60, "trend": "Bullish"},
        "NVDA": {"rsi": 55, "trend": "Bullish"},
        "WLD": {"rsi": 45, "trend": "Bullish"},
        "SOL": {"rsi": 50, "trend": "Bullish"},
        "ETH": {"rsi": 58, "trend": "Bullish"},
        "IB01.L": {"rsi": 50, "trend": "Neutral"},
    }
    
    print(f"🔧 測試設定:")
    print(f"  - 總資產: ${total_value:,.2f}")
    print(f"  - 最小佔比閾值: {Config.ANALYSIS_MIN_PERCENTAGE * 100}%")
    print(f"  - Watchlist: {Config.ANALYSIS_WATCHLIST}")
    print(f"  - Skip List: {Config.ANALYSIS_SKIP_LIST}")
    print()
    
    print(f"📊 測試標的與市值:")
    for asset in portfolio_summary['assets']:
        symbol = asset['symbol']
        value = asset['market_value']
        percentage = (value / total_value * 100)
        print(f"  - {symbol}: ${value:,.2f} ({percentage:.2f}%)")
    print()
    
    # 執行篩選
    print("🔨 執行 _select_focus_symbols...")
    focus, summary = service._select_focus_symbols(portfolio_summary, tech_signals)
    
    print()
    print(f"📊 篩選結果:")
    print(f"  - 重點標的 (Focus): {focus}")
    print(f"  - 摘要標的 (Summary): {summary}")
    print()
    
    # 驗證結果
    all_passed = True
    
    # 1. Watchlist 標的應該在 focus 中（不受市值限制）
    for symbol in Config.ANALYSIS_WATCHLIST:
        if symbol in focus:
            print(f"  ✅ {symbol} 正確出現在 Focus 中（Watchlist，不受市值限制）")
        else:
            print(f"  ❌ {symbol} 應該在 Focus 中（Watchlist）")
            all_passed = False
    
    # 2. 大於 1% 的標的應該在 summary 中
    large_symbols = ["NVDA", "ETH"]  # 15% 和 1.25%
    for symbol in large_symbols:
        if symbol in summary:
            print(f"  ✅ {symbol} 正確出現在 Summary 中（佔比 > 1%）")
        else:
            print(f"  ❌ {symbol} 應該在 Summary 中（佔比 > 1%）")
            all_passed = False
    
    # 3. 小於 1% 的標的不應該出現在任何清單中
    small_symbols = ["WLD", "SOL"]  # 0.04% 和 0.075%
    for symbol in small_symbols:
        if symbol not in focus and symbol not in summary:
            print(f"  ✅ {symbol} 正確被過濾（佔比 < 1%）")
        else:
            print(f"  ❌ {symbol} 應該被過濾（佔比 < 1%）")
            all_passed = False
    
    # 4. Skip List 標的不應該出現在任何清單中
    if "IB01.L" not in focus and "IB01.L" not in summary:
        print(f"  ✅ IB01.L 正確被跳過（Skip List）")
    else:
        print(f"  ❌ IB01.L 應該被跳過（Skip List）")
        all_passed = False
    
    print()
    if all_passed:
        print("=" * 80)
        print("  ✅ 所有測試通過！市值佔比過濾功能正常運作")
        print("=" * 80)
    else:
        print("=" * 80)
        print("  ❌ 部分測試失敗")
        print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    test_min_percentage_filter()
