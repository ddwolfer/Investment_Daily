# -*- coding: utf-8 -*-
"""
測試 Telegram HTML 格式轉換
"""

from investment_bot.services.telegram_bot import TelegramBotService

def test_markdown_to_html_conversion():
    """測試 Markdown 到 HTML 的轉換"""
    print("="*80)
    print("  測試 Markdown 到 HTML 轉換")
    print("="*80)
    
    service = TelegramBotService()
    
    # 測試用的 Markdown 文字
    test_markdown = """
# 大標題測試
## 二級標題測試
### 三級標題測試

這是一段包含 **粗體文字** 和 *斜體文字* 的測試。

還有 `行內代碼` 的測試。

這是一個 [測試連結](https://example.com) 的範例。

**重點**:
- **TSLA**: RSI 65.43，建議持有
- **BTC**: RSI 78.50，建議減碼
"""
    
    # 轉換為 HTML
    html_result = service._markdown_to_html(test_markdown)
    
    print("\n--- Markdown 原文 ---")
    print(test_markdown)
    print("\n--- 轉換後的 HTML ---")
    print(html_result)
    print("\n" + "="*80)
    
    return html_result

def test_send_to_telegram():
    """測試實際發送到 Telegram"""
    print("\n" + "="*80)
    print("  測試發送到 Telegram")
    print("="*80)
    
    service = TelegramBotService()
    
    if not service.bot:
        print("  ❌ Bot 未初始化，無法測試")
        return False
    
    # 簡單的測試訊息
    test_message = """
# 📊 HTML 格式測試

這是一條測試訊息，用於驗證 **HTML 格式** 是否正常顯示。

## 測試項目

**粗體文字**、*斜體文字*、`代碼文字`

- ✅ 列表項目 1
- ✅ 列表項目 2

如果你看到格式化的文字，代表 HTML 模式運作正常！
"""
    
    print("\n  正在發送測試訊息到 Telegram...")
    result = service.send_report(test_message)
    
    if result:
        print("  ✅ 測試訊息發送成功！")
        print("  請檢查 Telegram 群組確認格式是否正確顯示")
    else:
        print("  ❌ 測試訊息發送失敗")
    
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  Telegram HTML 格式測試")
    print("="*80)
    
    # 測試 1: 轉換功能
    print("\n[1/2] 測試 Markdown → HTML 轉換")
    test_markdown_to_html_conversion()
    
    # 測試 2: 實際發送
    print("\n[2/2] 測試發送到 Telegram")
    test_send_to_telegram()
    
    print("\n" + "="*80)
    print("  測試完成")
    print("="*80)

