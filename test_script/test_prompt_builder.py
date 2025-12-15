# -*- coding: utf-8 -*-
"""
測試 LLM Prompt 組裝
專門用來展示最終的 Prompt 長什麼樣子
"""

import sys
sys.path.insert(0, '.')

from investment_bot.services.llm_analyzer import LLMAnalyzerService

def create_mock_data():
    """建立模擬數據（使用剛才測試的真實數據結構）"""
    
    # 模擬持倉摘要
    portfolio_summary = {
        "total_value": 54233.50,
        "assets": [
            {
                "symbol": "TSLA",
                "type": "Stock",
                "qty": 10,
                "current_price": 446.89,
                "market_value": 4468.90,
                "cost_basis": 200.00,
                "unrealized_pl": 2468.90,
                "return_rate": 1.234  # 123.4%
            },
            {
                "symbol": "NVDA",
                "type": "Stock",
                "qty": 50,
                "current_price": 180.93,
                "market_value": 9046.50,
                "cost_basis": 150.00,
                "unrealized_pl": 1546.50,
                "return_rate": 0.206  # 20.6%
            },
            {
                "symbol": "BTC",
                "type": "Crypto",
                "qty": 0.5,
                "current_price": 87874.79,
                "market_value": 43937.40,
                "cost_basis": 65000.00,
                "unrealized_pl": 11437.40,
                "return_rate": 0.352  # 35.2%
            }
        ]
    }
    
    # 模擬技術分析訊號
    tech_signals = {
        "TSLA": {
            "current_price": 446.89,
            "rsi": 65.43,
            "is_overbought": False,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {
                "fast": 440.21,
                "mid": 420.15,
                "slow": 390.50
            },
            "macd": {
                "line": 5.23,
                "signal": 3.45,
                "hist": 1.78
            },
            "bb": {
                "upper": 480.50,
                "lower": 410.30,
                "pct_b": 0.65
            }
        },
        "NVDA": {
            "current_price": 180.93,
            "rsi": 58.21,
            "is_overbought": False,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {
                "fast": 178.50,
                "mid": 165.30,
                "slow": 150.20
            },
            "macd": {
                "line": 2.15,
                "signal": 1.80,
                "hist": 0.35
            },
            "bb": {
                "upper": 195.00,
                "lower": 165.00,
                "pct_b": 0.53
            }
        },
        "BTC": {
            "current_price": 87874.79,
            "rsi": 78.50,
            "is_overbought": True,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {
                "fast": 86500.00,
                "mid": 82000.00,
                "slow": 75000.00
            },
            "macd": {
                "line": 3500.00,
                "signal": 3200.00,
                "hist": 300.00
            },
            "bb": {
                "upper": 92000.00,
                "lower": 78000.00,
                "pct_b": 0.87
            }
        }
    }
    
    # 模擬市場情緒（使用真實測試數據）
    market_sentiment = {
        "value": 16,
        "classification": "Extreme Fear"
    }
    
    return portfolio_summary, tech_signals, market_sentiment

def main():
    """主測試流程"""
    print("=" * 80)
    print("  LLM Prompt Builder 測試")
    print("  目的：展示完整的 Prompt 組裝結果")
    print("=" * 80)
    print()
    
    # 建立模擬數據
    print("📊 正在建立模擬數據...")
    portfolio_summary, tech_signals, market_sentiment = create_mock_data()
    print(f"  ✅ 持倉數量: {len(portfolio_summary['assets'])} 個")
    print(f"  ✅ 技術分析: {len(tech_signals)} 個標的")
    print(f"  ✅ 市場情緒: {market_sentiment['classification']}")
    print()
    
    # 初始化 LLM 服務（不需要 API Key，只測試 Prompt 組裝）
    print("🔧 正在初始化 LLM 服務...")
    llm_service = LLMAnalyzerService()
    print()
    
    # 組裝 Prompt
    print("🔨 正在組裝 Prompt...")
    prompt = llm_service._build_prompt(portfolio_summary, tech_signals, market_sentiment)
    print(f"  ✅ Prompt 長度: {len(prompt)} 字元")
    print(f"  ✅ 估算 Token 數: ~{len(prompt) // 3} tokens (粗估)")
    print()
    
    # 顯示完整 Prompt
    print("=" * 80)
    print("  完整 Prompt 內容")
    print("=" * 80)
    print()
    print(prompt)
    print()
    print("=" * 80)
    print("  Prompt 展示完成")
    print("=" * 80)
    
    # 統計資訊
    print()
    print("📊 Prompt 結構統計:")
    print(f"  - 總字元數: {len(prompt)}")
    print(f"  - 總行數: {len(prompt.split(chr(10)))}")
    print(f"  - 包含區塊: 系統角色、持倉數據、技術指標、市場情緒、輸出要求")
    print()

if __name__ == "__main__":
    main()

