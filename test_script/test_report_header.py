# -*- coding: utf-8 -*-
"""
測試報告頭部功能（日期自動添加）
"""

from datetime import datetime
from investment_bot.services.telegram_bot import TelegramBotService

def test_header_generation():
    """測試報告頭部生成"""
    print("="*80)
    print("  測試報告頭部生成功能")
    print("="*80)
    
    service = TelegramBotService()
    
    # 模擬 LLM 生成的報告內容（不包含標題和日期）
    llm_report = """
<b>⚠️ 1. 風險警示</b>

以下是需要立即關注的問題：
  - <b>TSLA</b>: RSI 65.43 處於健康區間，無立即風險
  - 市場情緒處於極度恐慌狀態

<b>🎯 2. 操作建議</b>

<b>2.1 重點分析標的</b>
  - <b>TSLA</b>: 建議持有
"""
    
    print("\n--- LLM 生成的原始報告（無頭部）---")
    print(llm_report[:200] + "...")
    
    # 添加頭部
    report_with_header = service._add_report_header(llm_report)
    
    print("\n--- 添加頭部後的完整報告 ---")
    lines = report_with_header.split('\n')[:15]
    for line in lines:
        print(line)
    print("...")
    
    # 驗證
    current_date = datetime.now().strftime('%Y年%m月%d日')
    current_year = datetime.now().strftime('%Y年')
    
    has_title = '專業技術分析日報' in report_with_header
    has_date = current_date in report_with_header or current_year in report_with_header
    has_weekday = any(day in report_with_header for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
    has_analyst = '分析師' in report_with_header
    has_separator = '───' in report_with_header
    has_original_content = '風險警示' in report_with_header
    
    print("\n--- 驗證結果 ---")
    print(f"  包含報告標題: {'✅' if has_title else '❌'}")
    print(f"  包含實際日期: {'✅' if has_date else '❌'}")
    print(f"  包含星期資訊: {'✅' if has_weekday else '❌'}")
    print(f"  包含分析師資訊: {'✅' if has_analyst else '❌'}")
    print(f"  包含分隔線: {'✅' if has_separator else '❌'}")
    print(f"  保留原始內容: {'✅' if has_original_content else '❌'}")
    
    all_ok = has_title and has_date and has_weekday and has_analyst and has_separator and has_original_content
    
    if all_ok:
        print("\n  🎉 報告頭部生成成功！")
    else:
        print("\n  ❌ 報告頭部生成失敗")
    
    return all_ok

def test_send_with_header():
    """測試發送帶頭部的報告到 Telegram"""
    print("\n" + "="*80)
    print("  測試發送帶頭部的報告")
    print("="*80)
    
    service = TelegramBotService()
    
    if not service.bot:
        print("  ❌ Bot 未初始化，無法測試")
        return False
    
    # 模擬 LLM 生成的簡短報告
    test_report = """
<b>⚠️ 1. 風險警示</b>

目前無重大風險警示。

<b>🎯 2. 操作建議</b>

<b>2.1 重點分析標的</b>
  - <b>測試標的</b>: 這是一條測試訊息
  - 用於驗證報告頭部功能是否正常運作

<b>🌍 3. 市場情緒分析</b>

市場情緒正常。

<b>📋 4. 今日重點關注</b>

無特殊關注事項。

<i>這是一條測試報告，用於驗證日期頭部自動添加功能</i>
"""
    
    print("\n  正在發送測試報告到 Telegram...")
    print("  （會自動添加日期頭部）")
    
    result = service.send_report(test_report)
    
    if result:
        print("  ✅ 測試報告發送成功！")
        print("\n  請到 Telegram 檢查：")
        print("    1. 報告開頭是否有「專業技術分析日報」")
        print("    2. 報告日期是否為今天的實際日期")
        print("    3. 報告日期是否包含星期資訊")
        print("    4. 是否有分隔線")
        print("    5. LLM 生成的內容是否正常顯示")
    else:
        print("  ❌ 測試報告發送失敗")
    
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  報告頭部功能測試")
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
    
    # 測試 1: 頭部生成
    print("\n[1/2] 測試報告頭部生成")
    header_ok = test_header_generation()
    
    # 測試 2: 發送到 Telegram
    print("\n[2/2] 測試發送到 Telegram")
    send_ok = test_send_with_header()
    
    # 總結
    print("\n" + "="*80)
    print("  測試總結")
    print("="*80)
    print(f"  頭部生成: {'✅ 通過' if header_ok else '❌ 失敗'}")
    print(f"  發送測試: {'✅ 通過' if send_ok else '❌ 失敗'}")
    
    if header_ok and send_ok:
        print("\n  🎉 所有測試通過！日期會正確顯示")
    else:
        print("\n  ❌ 部分測試失敗，請檢查")
    
    print("="*80)

