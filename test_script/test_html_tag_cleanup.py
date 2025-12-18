# -*- coding: utf-8 -*-
"""
測試 Telegram HTML 標籤清理功能
"""

from investment_bot.services.telegram_bot import TelegramBotService

def test_tag_cleanup():
    """測試不支援標籤的清理"""
    print("="*80)
    print("  測試 HTML 標籤清理功能")
    print("="*80)
    
    service = TelegramBotService()
    
    # 測試包含不支援標籤的 HTML
    test_html = """
<h2>這是標題（不支援）</h2>
<p>這是段落（不支援）</p>

<b>支援的粗體</b>和<i>支援的斜體</i>

<ul>
    <li>列表項目 1（不支援）</li>
    <li>列表項目 2（不支援）</li>
</ul>

<hr>

<code>支援的代碼</code>

<div>容器標籤（不支援）</div>
"""
    
    print("\n--- 原始 HTML ---")
    print(test_html)
    
    # 清理標籤
    cleaned = service._clean_unsupported_html_tags(test_html)
    
    print("\n--- 清理後的 HTML ---")
    print(cleaned)
    
    # 檢查是否還有不支援的標籤
    unsupported_tags = ['<h1>', '<h2>', '<h3>', '<ul>', '<ol>', '<li>', '<p>', '<hr>', '<div>']
    found_unsupported = []
    for tag in unsupported_tags:
        if tag.lower() in cleaned.lower():
            found_unsupported.append(tag)
    
    print("\n" + "="*80)
    print("  檢查結果")
    print("="*80)
    
    if found_unsupported:
        print(f"  ⚠️  仍包含不支援的標籤: {', '.join(found_unsupported)}")
        return False
    else:
        print("  ✅ 所有不支援的標籤已清理")
    
    # 檢查是否保留支援的標籤
    supported_tags_found = '<b>' in cleaned and '<i>' in cleaned and '<code>' in cleaned
    if supported_tags_found:
        print("  ✅ 支援的標籤(<b>, <i>, <code>)已保留")
    else:
        print("  ⚠️  支援的標籤可能被誤刪")
    
    return not found_unsupported and supported_tags_found

def test_send_cleaned_html():
    """測試發送清理後的 HTML 到 Telegram"""
    print("\n" + "="*80)
    print("  測試發送清理後的 HTML 到 Telegram")
    print("="*80)
    
    service = TelegramBotService()
    
    if not service.bot:
        print("  ❌ Bot 未初始化，無法測試")
        return False
    
    # 包含不支援標籤的測試訊息
    test_message = """
<h2>📊 HTML 標籤清理測試</h2>

這是一條測試訊息，用於驗證 <b>HTML 標籤清理</b> 功能。

<h3>測試項目</h3>

<ul>
    <li><b>粗體文字</b>（支援）</li>
    <li><i>斜體文字</i>（支援）</li>
    <li><code>代碼文字</code>（支援）</li>
</ul>

---
<b>⚠️ 1. 風險警示</b>

- <b>RSI 超買警示</b>：
  - GLD (黃金 ETF)：RSI 72.00，已進入超買區間，短期存在回調風險，建議獲利了結。
- <b>趨勢轉弱與死亡交叉</b>：
  - BTC (比特幣)：EMA 排列為空頭（20 &lt; 60 &lt; 120），確認趨勢轉弱，價格跌破所有關鍵均線支撐。
  - ETH (以太幣)：EMA 排列空頭，MACD 處於空頭，趨勢持續下行。
  - IVV (標普 ETF)：MACD 柱狀體轉負 (-0.88)，顯示短期上漲動能正在消退。
- <b>布林通道突破</b>：
  - 目前所有重點分析標的價格均位於布林通道內，無立即突破通道的風險。

<b>整體風險總結</b>：整體風險等級為中等偏高。主要風險點集中在貴金屬（GLD）的超買，以及主要加密貨幣（BTC, ETH）的技術面弱化和趨勢確認轉空。市場情緒處於極度恐慌，可能加劇賣壓。

---

<hr>

<p>如果你看到這則訊息，且格式正常，代表標籤清理功能運作正常！</p>
"""
    
    print("\n  正在發送測試訊息到 Telegram...")
    print("  （會自動清理不支援的標籤）")
    
    result = service.send_report(test_message)
    
    if result:
        print("  ✅ 測試訊息發送成功！")
        print("  請檢查 Telegram 群組確認：")
        print("    1. 是否看到格式化文字（粗體、斜體、代碼）")
        print("    2. 是否沒有顯示 HTML 標籤本身")
    else:
        print("  ❌ 測試訊息發送失敗")
    
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  Telegram HTML 標籤清理測試")
    print("="*80)
    
    # 測試 1: 標籤清理
    print("\n[1/2] 測試標籤清理功能")
    cleanup_ok = test_tag_cleanup()
    
    # 測試 2: 實際發送
    print("\n[2/2] 測試發送到 Telegram")
    send_ok = test_send_cleaned_html()
    
    print("\n" + "="*80)
    print("  測試總結")
    print("="*80)
    print(f"  標籤清理: {'✅ 通過' if cleanup_ok else '❌ 失敗'}")
    print(f"  發送測試: {'✅ 通過' if send_ok else '❌ 失敗'}")
    print("="*80)

