# -*- coding: utf-8 -*-
"""
Telegram Bot ?? (Telegram Bot Service)
鞎痊撠??? Markdown ?勗??潮????Telegram Chat??
"""

import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from ..config import Config

class TelegramBotService:
    def __init__(self):
        """????Telegram Bot ??"""
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        
        if not self.token or not self.chat_id:
            print("霅血?: ?芾身摰?Telegram Token ??Chat ID??)

    async def send_message_async(self, message):
        """??甇亦????""
        if not self.token or not self.chat_id:
            print("?⊥??潮? 蝻箏? Token ??Chat ID")
            return

        try:
            bot = Bot(token=self.token)
            # 雿輻 Markdown 璅∪?
            # 閮鳴?LLM ????Markdown ???航??芾?蝢拍?摮泵撠 ParseMode.MARKDOWN_V2 ?梢
            # ParseMode.MARKDOWN (V1) 瘥?撖砍捆雿??質?撠??摰 legacy mode
            # ?箔?摰韏瑁?嚗??仃?????箇???
            await bot.send_message(chat_id=self.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
            print("Telegram 閮?潮???")
        except Exception as e:
            print(f"Telegram Markdown ?潮仃?? {e}")
            # 憒? Markdown 閫??憭望?嚗?閰衣?亦????
            try:
                print("?岫隞亦????潮?..")
                await bot.send_message(chat_id=self.chat_id, text=message)
                print("蝝?摮??舐????")
            except Exception as e2:
                print(f"蝝?摮??憭望?: {e2}")

    def send_report(self, report_text):
        """?郊隤輻?亙 (靘?main.py 雿輻)"""
        if not report_text:
            print("?勗??批捆?箇征嚗??潮?)
            return
            
        try:
            # ?冽?鈭憓? (憒?Jupyter) ?ㄐ?航??蝒?雿?函? script 銝剜璅???
            asyncio.run(self.send_message_async(report_text))
        except Exception as e:
            print(f"?瑁? asyncio loop 憭望?: {e}")

