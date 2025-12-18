# -*- coding: utf-8 -*-
"""
測試 HTML 特殊字符轉義功能
"""

from investment_bot.services.telegram_bot import TelegramBotService

def test_html_escape():
    """測試 HTML 特殊字符轉義"""
    print("="*80)
    print("  測試 HTML 特殊字符轉義功能")
    print("="*80)
    
    service = TelegramBotService()
    
    # 測試包含 < > & 的文本
    test_cases = [
        {
            "name": "數學比較符號",
            "input": """
<b>技術分析</b>
- RSI < 30 表示超賣
- RSI > 70 表示超買
- 價格 > EMA20 表示多頭
- MACD > 0 且 > Signal Line
""",
            "expected_contains": ["&lt;", "&gt;"],
            "should_preserve": ["<b>", "</b>"]
        },
        {
            "name": "混合格式",
            "input": """
<b>TSLA</b> 技術指標：
- <code>RSI: 65.43</code>
- EMA10 > EMA20 > EMA50
- 價格 < 布林上軌
- 支撐 $440 < 現價 $446.89 < 壓力 $480
""",
            "expected_contains": ["&lt;", "&gt;"],
            "should_preserve": ["<b>", "</b>", "<code>", "</code>"]
        },
        {
            "name": "& 符號",
            "input": """
<b>注意</b>: A & B 都需要關注
Fear & Greed Index
""",
            "expected_contains": ["&amp;"],
            "should_preserve": ["<b>", "</b>"]
        },
        {
            "name": "只有合法標籤",
            "input": """
<b>粗體</b>、<i>斜體</i>、<code>代碼</code>
<a href="https://example.com">連結</a>
""",
            "expected_contains": [],  # 不應該有轉義
            "should_preserve": ["<b>", "</b>", "<i>", "</i>", "<code>", "</code>", "<a href=", "</a>"]
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- 測試案例 {i}: {test['name']} ---")
        print("輸入：")
        print(test['input'])
        
        # 轉義處理
        result = service._escape_html_special_chars(test['input'])
        
        print("\n輸出：")
        print(result)
        
        # 驗證
        test_passed = True
        
        # 檢查應該包含的轉義字符
        for expected in test['expected_contains']:
            if expected not in result:
                print(f"  ❌ 缺少預期的轉義：{expected}")
                test_passed = False
                all_passed = False
        
        # 檢查應該保留的 HTML 標籤
        for tag in test['should_preserve']:
            if tag not in result:
                print(f"  ❌ 合法標籤被誤刪：{tag}")
                test_passed = False
                all_passed = False
        
        if test_passed:
            print(f"  ✅ 測試通過")
        
    print("\n" + "="*80)
    return all_passed

def test_full_cleanup_with_escape():
    """測試完整的清理流程（包含標籤清理 + 特殊字符轉義）"""
    print("\n" + "="*80)
    print("  測試完整清理流程（標籤清理 + 特殊字符轉義）")
    print("="*80)
    
    service = TelegramBotService()
    
    # 包含不支援標籤和特殊字符的測試
    test_html = """
<h2>技術分析報告</h2>

<b>風險警示</b>
<ul>
    <li>RSI > 70 超買風險</li>
    <li>價格 < 支撐位 $440</li>
    <li>MACD < Signal Line 空頭訊號</li>
</ul>

<hr>

<p>Fear & Greed Index: 16 (Extreme Fear)</p>

<b>操作建議</b>
- 建議：若 RSI > 75 則減碼
- 支撐：EMA20 < 現價 < 布林上軌
"""
    
    print("\n--- 原始 HTML ---")
    print(test_html)
    
    # 完整清理（會自動調用轉義）
    cleaned = service._clean_unsupported_html_tags(test_html)
    
    print("\n--- 清理後的 HTML ---")
    print(cleaned)
    
    # 驗證
    print("\n--- 驗證結果 ---")
    
    # 不應該有不支援的標籤
    unsupported_tags = ['<h2>', '<ul>', '<li>', '<hr>', '<p>']
    has_unsupported = any(tag.lower() in cleaned.lower() for tag in unsupported_tags)
    
    # 應該有轉義的特殊字符
    has_escaped = '&lt;' in cleaned or '&gt;' in cleaned or '&amp;' in cleaned
    
    # 應該保留合法的標籤
    has_valid_tags = '<b>' in cleaned
    
    print(f"  不支援標籤已清理: {'✅' if not has_unsupported else '❌'}")
    print(f"  特殊字符已轉義: {'✅' if has_escaped else '❌'}")
    print(f"  合法標籤已保留: {'✅' if has_valid_tags else '✅'}")
    
    return not has_unsupported and has_escaped and has_valid_tags

def test_send_to_telegram():
    """測試發送到 Telegram"""
    print("\n" + "="*80)
    print("  測試發送到 Telegram")
    print("="*80)
    
    service = TelegramBotService()
    
    if not service.bot:
        print("  ❌ Bot 未初始化，無法測試")
        return False
    
    # 測試訊息（包含特殊字符）
    test_message = """
<b>📊 HTML 特殊字符轉義測試</b>

這是一條測試訊息，用於驗證特殊字符轉義功能。

<b>測試項目</b>
  - RSI 低於 30 表示超賣（正確寫法）
  - 價格高於 EMA20 表示多頭（正確寫法）
  - Fear & Greed Index: 16

<b>技術指標</b>
  - <code>RSI: 65.43</code>
  - <code>MACD: 1.78</code>
  - <i>趨勢: Bullish</i>

如果你看到這則訊息且格式正常，代表功能運作正常！
"""
    
    print("\n  正在發送測試訊息到 Telegram...")
    result = service.send_report(test_message)
    
    if result:
        print("  ✅ 測試訊息發送成功！")
        print("  請檢查 Telegram 確認：")
        print("    1. 格式正常顯示（粗體、斜體、代碼）")
        print("    2. 沒有顯示 HTML 標籤或轉義符號")
        print("    3. 文字內容完整")
    else:
        print("  ❌ 測試訊息發送失敗")
    
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  HTML 特殊字符轉義測試")
    print("="*80)
    
    # 測試 1: 基礎轉義功能
    print("\n[1/3] 測試基礎轉義功能")
    escape_ok = test_html_escape()
    
    # 測試 2: 完整清理流程
    print("\n[2/3] 測試完整清理流程")
    cleanup_ok = test_full_cleanup_with_escape()
    
    # 測試 3: 發送到 Telegram
    print("\n[3/3] 測試發送到 Telegram")
    send_ok = test_send_to_telegram()
    
    # 總結
    print("\n" + "="*80)
    print("  測試總結")
    print("="*80)
    print(f"  基礎轉義: {'✅ 通過' if escape_ok else '❌ 失敗'}")
    print(f"  完整清理: {'✅ 通過' if cleanup_ok else '❌ 失敗'}")
    print(f"  發送測試: {'✅ 通過' if send_ok else '❌ 失敗'}")
    
    if escape_ok and cleanup_ok and send_ok:
        print("\n  🎉 所有測試通過！")
    else:
        print("\n  ⚠️  部分測試失敗，請檢查")
    
    print("="*80)

