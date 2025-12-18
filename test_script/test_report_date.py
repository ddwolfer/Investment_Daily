# -*- coding: utf-8 -*-
"""
測試 LLM 報告日期顯示功能
"""

from datetime import datetime
from investment_bot.services.llm_analyzer import LLMAnalyzerService

def test_date_in_prompt():
    """測試 Prompt 中是否包含當前日期"""
    print("="*80)
    print("  測試 Prompt 中的日期資訊")
    print("="*80)
    
    llm_service = LLMAnalyzerService()
    
    # 準備測試數據
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
    
    # 組裝 Prompt
    prompt = llm_service._build_prompt(portfolio_summary, tech_signals, sentiment)
    
    # 檢查 Prompt 中是否包含日期
    print("\n  正在檢查 Prompt...")
    
    # 獲取當前日期（用於比對）
    current_date = datetime.now().strftime('%Y年%m月%d日')
    current_year = datetime.now().strftime('%Y年')
    
    has_date = current_date in prompt or current_year in prompt
    has_weekday = any(day in prompt for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
    has_today_marker = '今天是' in prompt
    
    print(f"\n  ✅ Prompt 包含日期資訊: {'是' if has_date else '否'}")
    print(f"  ✅ Prompt 包含星期資訊: {'是' if has_weekday else '否'}")
    print(f"  ✅ Prompt 包含「今天是」標記: {'是' if has_today_marker else '否'}")
    
    # 顯示 Prompt 中與日期相關的部分（前 500 字元）
    print("\n  --- Prompt 前 500 字元 ---")
    print(prompt[:500])
    print("  ...")
    
    return has_date and has_weekday and has_today_marker

def test_date_in_report():
    """測試生成的報告中是否包含正確的日期"""
    print("\n" + "="*80)
    print("  測試生成報告中的日期")
    print("="*80)
    
    llm_service = LLMAnalyzerService()
    
    if not llm_service.client:
        print("  ❌ Gemini 服務未初始化，無法測試")
        return False
    
    # 準備測試數據
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
    
    # 檢查報告中的日期
    current_date = datetime.now().strftime('%Y年%m月%d日')
    current_year = datetime.now().strftime('%Y年')
    current_month = datetime.now().strftime('%m月')
    
    has_date = current_date in report or (current_year in report and current_month in report)
    has_placeholder = '[當前日期]' in report or '[今日日期]' in report or '[日期]' in report
    has_weekday = any(day in report for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
    
    print("\n  --- 日期檢查結果 ---")
    print(f"  包含實際日期: {'✅ 是' if has_date else '❌ 否'}")
    print(f"  包含星期資訊: {'✅ 是' if has_weekday else '⚠️  否'}")
    print(f"  包含日期佔位符: {'❌ 是（應避免）' if has_placeholder else '✅ 否（正確）'}")
    
    # 顯示報告開頭部分
    print("\n  --- 報告開頭部分 ---")
    lines = report.split('\n')[:15]
    for line in lines:
        print(f"  {line}")
    
    if has_placeholder:
        print("\n  ⚠️  警告：報告中仍包含日期佔位符，LLM 可能未正確使用提供的日期")
    
    return has_date and not has_placeholder

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  LLM 報告日期功能測試")
    print("="*80)
    
    # 顯示當前日期
    current_date = datetime.now().strftime('%Y年%m月%d日')
    current_weekday = datetime.now().strftime('%A')
    weekday_cn = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日'
    }.get(current_weekday, '')
    
    print(f"\n  當前日期: {current_date} ({weekday_cn})")
    
    # 測試 1: Prompt 中的日期
    print("\n[1/2] 測試 Prompt 中的日期資訊")
    prompt_ok = test_date_in_prompt()
    
    # 測試 2: 生成報告中的日期
    print("\n[2/2] 測試生成報告中的日期")
    report_ok = test_date_in_report()
    
    # 總結
    print("\n" + "="*80)
    print("  測試總結")
    print("="*80)
    print(f"  Prompt 日期: {'✅ 通過' if prompt_ok else '❌ 失敗'}")
    print(f"  報告日期: {'✅ 通過' if report_ok else '❌ 失敗'}")
    
    if prompt_ok and report_ok:
        print("\n  🎉 所有測試通過！報告會顯示正確的日期")
    elif prompt_ok and not report_ok:
        print("\n  ⚠️  Prompt 已提供日期，但 LLM 未正確使用")
        print("  建議：可能需要調整 Prompt 以更明確要求使用實際日期")
    else:
        print("\n  ❌ 測試失敗，請檢查代碼")
    
    print("="*80)

