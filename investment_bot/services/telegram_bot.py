# -*- coding: utf-8 -*-
"""
Telegram Bot 服務 (Telegram Bot Service)
負責將生成的 Markdown 報告發送到指定的 Telegram Chat。
"""

import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from ..config import Config

class TelegramBotService:
    def __init__(self):
        """初始化 Telegram Bot 服務"""
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        
        if not self.token or not self.chat_id:
            print("警告: 未設定 Telegram Token 或 Chat ID。")

    async def send_message_async(self, message):
        """非同步發送訊息"""
        if not self.token or not self.chat_id:
            print("無法發送: 缺少 Token 或 Chat ID")
            return

        try:
            bot = Bot(token=self.token)
            # 使用 Markdown 模式
            # 註：LLM 生成的 Markdown 有時可能包含未轉義的字符導致 ParseMode.MARKDOWN_V2 報錯
            # ParseMode.MARKDOWN (V1) 比較寬容但功能較少，雖然它是 legacy mode
            # 為了安全起見，如果失敗則降級為純文字
            await bot.send_message(chat_id=self.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
            print("Telegram 訊息發送成功！")
        except Exception as e:
            print(f"Telegram Markdown 發送失敗: {e}")
            # 如果 Markdown 解析失敗，嘗試直接發送純文字
            try:
                print("嘗試以純文字發送...")
                await bot.send_message(chat_id=self.chat_id, text=message)
                print("純文字訊息發送成功！")
            except Exception as e2:
                print(f"純文字發送也失敗: {e2}")

    def send_report(self, report_text):
        """同步調用接口 (供 main.py 使用)"""
        if not report_text:
            print("報告內容為空，不發送。")
            return
            
        try:
            # 在某些環境下 (如 Jupyter) 這裡可能會衝突，但在獨立 script 中是標準做法
            asyncio.run(self.send_message_async(report_text))
        except Exception as e:
            print(f"執行 asyncio loop 失敗: {e}")

