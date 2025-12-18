# -*- coding: utf-8 -*-
"""
測試 LLM Analyzer 是否生成 HTML 格式報告
"""

from investment_bot.services.llm_analyzer import LLMAnalyzerService

def test_llm_html_output():
    """測試 LLM 生成 HTML 格式報告"""
    print("="*80)
    print("  測試 LLM Analyzer HTML 格式輸出")
    print("="*80)
    
    # 初始化服務
    llm_service = LLMAnalyzerService()
    
    if not llm_service.client:
        print("  ❌ Gemini 服務未初始化")
        return False
    
    # 組裝簡單測試數據
    portfolio_summary = {
        'total_value': 100000,
        'assets': [
            {
                'symbol': 'TSLA',
                'type': 'Stock',
                'qty': 10,
                'current_price': 446.89,
                'market_value': 4468.9,
                'cost_basis': 400,
                'unrealized_pl': 468.9,
                'return_rate': 0.117
            }
        ]
    }
    
    tech_signals = {
        'TSLA': {
            'symbol': 'TSLA',
            'current_price': 446.89,
            'indicators': {
                'rsi': 65.43,
                'ema_10': 445.21,
                'ema_20': 440.21,
                'ema_50': 435.00,
                'macd_line': 2.34,
                'signal_line': 1.56,
                'macd_histogram': 1.78,
                'bb_upper': 480.50,
                'bb_middle': 446.89,
                'bb_lower': 413.28,
                'bb_percent': 0.50
            },
            'trend': 'Bullish'
        }
    }
    
    sentiment = {
        'value': 16,
        'classification': 'Extreme Fear'
    }
    
    print("\n  正在呼叫 Gemini API 生成報告...")
    print("  ⏳ 請稍候...")
    
    # 生成報告
    report = llm_service.generate_report(portfolio_summary, tech_signals, sentiment)
    
    if not report:
        print("  ❌ 報告生成失敗")
        return False
    
    print(f"\n  ✅ 報告生成成功")
    print(f"  報告長度: {len(report)} 字元")
    
    # 檢查是否包含 HTML 標籤
    has_html_tags = '<b>' in report or '<i>' in report or '<code>' in report
    has_markdown = '**' in report or '__' in report or '##' in report
    
    print("\n" + "="*80)
    print("  格式檢測")
    print("="*80)
    print(f"  包含 HTML 標籤 (<b>, <i>, <code>): {'✅ 是' if has_html_tags else '❌ 否'}")
    print(f"  包含 Markdown 語法 (**, ##, __): {'⚠️  是' if has_markdown else '✅ 否'}")
    
    # 顯示前 1000 字元
    print("\n" + "="*80)
    print("  生成的報告預覽（前 1000 字元）")
    print("="*80)
    print(report[:1000])
    print("\n... (完整報告共 {} 字元)".format(len(report)))
    print("="*80)
    
    if has_html_tags and not has_markdown:
        print("\n  ✅ 測試通過：LLM 成功生成 HTML 格式報告")
        return True
    elif has_markdown:
        print("\n  ⚠️  警告：報告中仍包含 Markdown 語法")
        print("  建議檢查 Prompt 是否正確要求 HTML 格式")
        return False
    else:
        print("\n  ❌ 測試失敗：報告格式不符合預期")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  LLM HTML 格式輸出測試")
    print("="*80)
    
    test_llm_html_output()
    
    print("\n" + "="*80)
    print("  測試完成")
    print("="*80)

