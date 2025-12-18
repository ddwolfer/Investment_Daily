# -*- coding: utf-8 -*-
"""
Telegram Topic ID 獲取工具
用於幫助用戶找到群組中特定 Topic 的 ID
"""

import sys
sys.path.insert(0, '.')

from investment_bot.services.telegram_bot import TelegramBotService
from investment_bot.config import Config

def main():
    print("="*80)
    print("  Telegram Topic ID 獲取工具")
    print("="*80)
    print()
    
    # 檢查配置
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ 錯誤: 未設定 TELEGRAM_BOT_TOKEN")
        print("請在 .env 中設定 TELEGRAM_BOT_TOKEN")
        return
    
    if not Config.TELEGRAM_CHAT_ID:
        print("❌ 錯誤: 未設定 TELEGRAM_CHAT_ID")
        print("請在 .env 中設定 TELEGRAM_CHAT_ID")
        return
    
    print("📋 使用步驟:")
    print("  1. 在 Telegram 群組中找到你想要發送訊息的 Topic")
    print("  2. 在該 Topic 中發送一則訊息給 Bot（例如：/start 或任何文字）")
    print("  3. 執行此腳本")
    print("  4. 腳本會顯示該 Topic 的 ID")
    print("  5. 將 Topic ID 加入 .env 檔案: TELEGRAM_TOPIC_ID=<顯示的數字>")
    print()
    
    input("按 Enter 繼續...")
    print()
    
    # 初始化服務
    print("🔧 初始化 Telegram Bot...")
    service = TelegramBotService()
    
    if not service.bot:
        print("❌ Bot 初始化失敗")
        return
    
    # 獲取 Topic 資訊
    service.get_topic_info()
    
    print()
    print("="*80)
    print("  完成")
    print("="*80)
    print()
    print("💡 提示:")
    print("  - 如果看到 Topic ID，將它加入 .env:")
    print("    TELEGRAM_TOPIC_ID=<顯示的數字>")
    print("  - 如果沒有看到 Topic ID:")
    print("    1. 確認你在群組的 Topic 中發送了訊息")
    print("    2. 確認 Bot 已加入該群組")
    print("    3. 確認群組已啟用 Topics 功能")

if __name__ == "__main__":
    main()

