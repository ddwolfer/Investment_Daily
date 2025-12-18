# -*- coding: utf-8 -*-
"""
Telegram Bot 服務 (Telegram Bot Service)
負責推送 Markdown 格式報告到指定 Telegram Chat
"""

import asyncio
from telegram import Bot
from telegram.error import TelegramError, RetryAfter, TimedOut
from telegram.constants import ParseMode
from ..config import Config

class TelegramBotService:
    def __init__(self):
        """初始化 Telegram Bot 服務"""
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.bot = None
        
        if not self.token:
            print("  [Telegram] 警告: 未設定 TELEGRAM_BOT_TOKEN")
        elif not self.chat_id:
            print("  [Telegram] 警告: 未設定 TELEGRAM_CHAT_ID")
        else:
            try:
                self.bot = Bot(token=self.token)
                print(f"  [Telegram] Bot 初始化成功")
            except Exception as e:
                print(f"  [Telegram] Bot 初始化失敗: {e}")
    
    def send_report(self, report_text):
        """
        推送報告到 Telegram（同步包裝）
        
        Args:
            report_text: 報告內容 (Markdown 格式)
        
        Returns:
            bool: 是否發送成功
        """
        if not report_text:
            print("  [Telegram] 報告內容為空，取消推送")
            return False
        
        if not self.bot:
            print("  [Telegram] Bot 未初始化，無法推送")
            return False
        
        # 使用 asyncio 執行異步函數
        try:
            # 嘗試獲取現有事件循環，如果不存在則創建新的
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self._send_message_async(report_text))
            return result
        except Exception as e:
            print(f"  [Telegram] 推送失敗: {e}")
            return False
    
    async def _send_message_async(self, text):
        """
        異步發送訊息到 Telegram
        
        Args:
            text: 訊息內容
        
        Returns:
            bool: 是否發送成功
        """
        # 檢查訊息長度（Telegram 限制 4096 字元）
        if len(text) > 4096:
            print(f"  [Telegram] 警告: 訊息過長 ({len(text)} 字元)，將分段發送")
            return await self._send_long_message(text)
        
        # 嘗試發送訊息（帶重試機制）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"  [Telegram] 正在發送訊息 (嘗試 {attempt + 1}/{max_retries})...")
                
                # 發送訊息
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                
                print(f"  [Telegram] ✅ 訊息發送成功 (Message ID: {message.message_id})")
                return True
                
            except RetryAfter as e:
                # Telegram 要求稍後重試
                wait_time = e.retry_after
                print(f"  [Telegram] ⚠️  Rate Limit，需等待 {wait_time} 秒...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    print(f"  [Telegram] ❌ 達到最大重試次數")
                    return False
                    
            except TimedOut:
                # 網路超時
                print(f"  [Telegram] ⚠️  網路超時")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"  [Telegram] ❌ 達到最大重試次數")
                    return False
                    
            except TelegramError as e:
                # Telegram API 錯誤（通常是格式問題）
                print(f"  [Telegram] ❌ Telegram API 錯誤: {e}")
                
                # 如果是 Markdown 格式錯誤，嘗試用純文字發送
                if "can't parse" in str(e).lower() or "markdown" in str(e).lower():
                    print(f"  [Telegram] 嘗試使用純文字模式發送...")
                    return await self._send_as_plain_text(text)
                else:
                    return False
                    
            except Exception as e:
                print(f"  [Telegram] ❌ 未預期的錯誤: {e}")
                return False
        
        return False
    
    async def _send_long_message(self, text):
        """
        分段發送長訊息
        
        Args:
            text: 完整訊息內容
        
        Returns:
            bool: 是否全部發送成功
        """
        # 按行分割，避免切斷重要內容
        lines = text.split('\n')
        
        chunks = []
        current_chunk = ""
        
        for line in lines:
            # 如果加上這行會超過限制，就先儲存當前 chunk
            if len(current_chunk) + len(line) + 1 > 4000:  # 留 96 字元緩衝
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += ("\n" if current_chunk else "") + line
        
        # 加入最後一個 chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        print(f"  [Telegram] 訊息分為 {len(chunks)} 段發送")
        
        # 依序發送每個 chunk
        for i, chunk in enumerate(chunks, 1):
            print(f"  [Telegram] 發送第 {i}/{len(chunks)} 段...")
            success = await self._send_message_async(chunk)
            
            if not success:
                print(f"  [Telegram] ❌ 第 {i} 段發送失敗")
                return False
            
            # 避免觸發 Rate Limit
            if i < len(chunks):
                await asyncio.sleep(0.5)
        
        print(f"  [Telegram] ✅ 所有分段發送完成")
        return True
    
    async def _send_as_plain_text(self, text):
        """
        使用純文字模式發送（當 Markdown 格式錯誤時）
        
        Args:
            text: 訊息內容
        
        Returns:
            bool: 是否發送成功
        """
        try:
            message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=None,  # 純文字模式
                disable_web_page_preview=True
            )
            
            print(f"  [Telegram] ✅ 使用純文字模式發送成功 (Message ID: {message.message_id})")
            return True
            
        except Exception as e:
            print(f"  [Telegram] ❌ 純文字模式也失敗: {e}")
            return False
    
    async def send_test_message(self):
        """
        發送測試訊息
        
        Returns:
            bool: 是否發送成功
        """
        test_message = """
🤖 **Telegram Bot 測試訊息**

這是一條測試訊息，用於驗證 Bot 連接。

**測試項目**:
- ✅ Markdown 格式
- ✅ Emoji 支援
- ✅ 繁體中文顯示

如果你看到這則訊息，代表 Bot 運作正常！
"""
        
        print("  [Telegram] 正在發送測試訊息...")
        return await self._send_message_async(test_message.strip())
    
    def test_connection(self):
        """
        測試 Telegram Bot 連接（同步包裝）
        
        Returns:
            bool: 是否連接成功
        """
        if not self.bot:
            print("  [Telegram] Bot 未初始化")
            return False
        
        try:
            # 嘗試獲取現有事件循環，如果不存在則創建新的
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.send_test_message())
            return result
        except Exception as e:
            print(f"  [Telegram] 連接測試失敗: {e}")
            return False
