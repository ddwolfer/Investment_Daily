# -*- coding: utf-8 -*-
"""
Telegram Bot 整合測試
測試項目：
1. Bot 配置檢查
2. 連接測試
3. 測試訊息發送
4. Markdown 格式測試
5. 完整報告發送
"""

import sys
sys.path.insert(0, '.')

from investment_bot.services.telegram_bot import TelegramBotService
from investment_bot.config import Config

def print_separator(title=""):
    """印出分隔線"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
    else:
        print('-'*80)

def test_configuration():
    """測試 Bot 配置"""
    print_separator("[1/6] 測試 Bot 配置")
    
    print("\n  檢查環境變數...")
    
    config_ok = True
    
    if Config.TELEGRAM_BOT_TOKEN:
        # 隱藏部分 Token
        masked_token = Config.TELEGRAM_BOT_TOKEN[:10] + "..." + Config.TELEGRAM_BOT_TOKEN[-4:]
        print(f"    ✅ TELEGRAM_BOT_TOKEN: {masked_token}")
    else:
        print(f"    ❌ TELEGRAM_BOT_TOKEN: 未設定")
        print(f"    ⚠️  請在 .env 中設定 TELEGRAM_BOT_TOKEN")
        config_ok = False
    
    if Config.TELEGRAM_CHAT_ID:
        print(f"    ✅ TELEGRAM_CHAT_ID: {Config.TELEGRAM_CHAT_ID}")
    else:
        print(f"    ❌ TELEGRAM_CHAT_ID: 未設定")
        print(f"    ⚠️  請在 .env 中設定 TELEGRAM_CHAT_ID")
        config_ok = False
    
    if Config.TELEGRAM_TOPIC_ID:
        print(f"    ✅ TELEGRAM_TOPIC_ID: {Config.TELEGRAM_TOPIC_ID} (將發送到指定 Topic)")
    else:
        print(f"    ℹ️  TELEGRAM_TOPIC_ID: 未設定 (將發送到主頻道)")
    
    return config_ok

def test_get_topic_id(service):
    """測試獲取 Topic ID（輔助工具）"""
    print_separator("[2/6] 獲取 Topic ID（可選）")
    
    if not service:
        print("\n    ⚠️  跳過（服務未初始化）")
        return
    
    print("\n  此步驟用於幫助你找到群組 Topic ID")
    print("  如果你不需要發送到特定 Topic，可以跳過\n")
    
    user_input = input("  是否要獲取 Topic ID？(y/n): ").strip().lower()
    
    if user_input == 'y':
        service.get_topic_info()
    else:
        print("  跳過 Topic ID 獲取")

def test_service_initialization():
    """測試服務初始化"""
    print_separator("[3/6] 測試服務初始化")
    
    print("\n  正在初始化 TelegramBotService...")
    
    try:
        service = TelegramBotService()
        
        if service.bot:
            print(f"    ✅ Bot 初始化成功")
            return service
        else:
            print(f"    ❌ Bot 初始化失敗（可能缺少配置）")
            return None
            
    except Exception as e:
        print(f"    ❌ 初始化錯誤: {e}")
        return None

def test_connection(service):
    """測試連接"""
    print_separator("[4/6] 測試連接")
    
    if not service:
        print("\n    ⚠️  跳過測試（服務未初始化）")
        return False
    
    print("\n  正在發送測試訊息到 Telegram...")
    print("  ⏳ 請稍候...\n")
    
    try:
        success = service.test_connection()
        
        if success:
            print(f"\n    ✅ 測試訊息發送成功")
            print(f"    ✅ 請檢查 Telegram 是否收到訊息")
            return True
        else:
            print(f"\n    ❌ 測試訊息發送失敗")
            return False
            
    except Exception as e:
        print(f"\n    ❌ 連接測試錯誤: {e}")
        return False

def test_markdown_format(service):
    """測試 Markdown 格式"""
    print_separator("[5/6] 測試 Markdown 格式")
    
    if not service:
        print("\n    ⚠️  跳過測試（服務未初始化）")
        return False
    
    print("\n  正在測試各種 Markdown 格式...")
    
    test_message = """
📊 **Markdown 格式測試**

### 1. 文字格式
- **粗體文字**
- *斜體文字*
- `程式碼`

### 2. 列表
✅ 項目一
✅ 項目二
✅ 項目三

### 3. Emoji
📈 上漲
📉 下跌
⚠️ 警告
💡 提示

### 4. 表格（Markdown 表格在 Telegram 中需特殊處理）
標的 | 價格 | 趨勢
TSLA | $446.89 | 📈
BTC | $87,874.79 | 📈

_測試完成_
"""
    
    try:
        print("  ⏳ 發送中...\n")
        success = service.send_report(test_message.strip())
        
        if success:
            print(f"    ✅ Markdown 格式測試訊息發送成功")
            print(f"    ✅ 請檢查 Telegram 中的格式是否正確")
            return True
        else:
            print(f"    ❌ Markdown 格式測試失敗")
            return False
            
    except Exception as e:
        print(f"    ❌ Markdown 測試錯誤: {e}")
        return False

def test_full_report(service):
    """測試完整報告發送"""
    print_separator("[6/6] 測試完整報告發送")
    
    if not service:
        print("\n    ⚠️  跳過測試（服務未初始化）")
        return False
    
    print("\n  正在準備完整報告...")
    
    # 使用簡化版報告（模擬 LLM 生成的格式）
    mock_report = """
# 📊 AI 投資日報

**生成時間**: 2025-12-15 23:00:00
**分析師**: 專業技術分析師

---

## 💰 投資組合總覽

- **總市值**: $54,233.50
- **持倉數量**: 3 個標的
- **整體報酬**: 優秀

---

## ⚠️ 風險警示

### 🔴 紅色警示
**BTC (比特幣)**: RSI 78.50 嚴重超買

### 🟡 黃色警示
**TSLA (特斯拉)**: 動能過強，需注意回檔

---

## 🎯 操作建議

### TSLA (特斯拉)
- **現價**: $446.89
- **建議**: 持有
- **理由**: RSI 65.43 健康區間，MACD 多頭排列
- **操作**: 繼續持有現有 10 股

### NVDA (輝達)
- **現價**: $180.93
- **建議**: 持有
- **理由**: 技術面穩健，趨勢良好
- **操作**: 繼續持有現有 50 股

### BTC (比特幣)
- **現價**: $87,874.79
- **建議**: 適度減碼
- **理由**: RSI 78.50 已超買，價格接近布林上軌
- **操作**: 建議減碼 20%（約 0.10 BTC）

---

## 🌍 市場情緒

**Fear & Greed Index**: 16 (Extreme Fear 😱)

市場處於極度恐慌狀態，可能是逢低佈局的機會。

---

## 📋 今日重點關注

1. **BTC**: 優先處理，執行減碼操作
2. **TSLA**: 關注 $440.21 支撐
3. **NVDA**: 穩定持有

---

_本報告由 AI 自動生成，僅供參考_
"""
    
    print(f"  報告長度: {len(mock_report)} 字元")
    print("  ⏳ 發送中...\n")
    
    try:
        success = service.send_report(mock_report.strip())
        
        if success:
            print(f"\n    ✅ 完整報告發送成功")
            print(f"    ✅ 請檢查 Telegram 是否收到完整報告")
            return True
        else:
            print(f"\n    ❌ 完整報告發送失敗")
            return False
            
    except Exception as e:
        print(f"\n    ❌ 報告發送錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試流程"""
    print("="*80)
    print("  Telegram Bot 整合測試")
    print("  測試訊息推送功能")
    print("="*80)
    
    # 測試 1: 配置檢查
    if not test_configuration():
        print("\n❌ 測試終止：Bot 配置不完整")
        print("請確認 .env 中已設定 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        return
    
    # 測試 2: 獲取 Topic ID（可選）
    # 注意：需要先初始化服務才能獲取 Topic ID
    temp_service = TelegramBotService()
    if temp_service and temp_service.bot:
        test_get_topic_id(temp_service)
    
    # 測試 3: 服務初始化
    service = test_service_initialization()
    if not service:
        print("\n❌ 測試終止：服務初始化失敗")
        return
    
    # 測試 4: 連接測試
    connection_ok = test_connection(service)
    
    # 測試 5: Markdown 格式
    markdown_ok = test_markdown_format(service)
    
    # 測試 6: 完整報告
    report_ok = test_full_report(service)
    
    # 總結
    print_separator("測試總結")
    
    print("\n  📊 測試結果:")
    print(f"    ✅ Bot 配置: 通過")
    print(f"    ✅ 服務初始化: 通過")
    print(f"    {'✅' if connection_ok else '❌'} 連接測試: {'通過' if connection_ok else '失敗'}")
    print(f"    {'✅' if markdown_ok else '❌'} Markdown 格式: {'通過' if markdown_ok else '失敗'}")
    print(f"    {'✅' if report_ok else '❌'} 完整報告: {'通過' if report_ok else '失敗'}")
    
    if connection_ok and markdown_ok and report_ok:
        print("\n  🎉 所有測試通過！Telegram Bot 運作正常")
        print("  ✅ 請檢查 Telegram 中是否收到所有測試訊息")
    elif connection_ok:
        print("\n  ⚠️  部分測試通過，但有些功能需要優化")
    else:
        print("\n  ❌ 連接測試失敗，請檢查：")
        print("      1. Bot Token 是否正確")
        print("      2. Chat ID 是否正確")
        print("      3. 網路連接是否正常")
        print("      4. Bot 是否已加入目標 Chat")
    
    print("\n" + "="*80)
    print("  測試完成")
    print("="*80)
    
    print("\n💡 提示：")
    print("  - 如果收到測試訊息，請確認格式是否正確")
    print("  - Markdown 表格在 Telegram 中可能顯示為純文字")
    print("  - 如有問題，Bot 會自動降級為純文字模式")

if __name__ == "__main__":
    main()






