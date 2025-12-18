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
        self.topic_id = Config.TELEGRAM_TOPIC_ID  # 群組 Topic ID (可選)
        self.bot = None
        
        if not self.token:
            print("  [Telegram] 警告: 未設定 TELEGRAM_BOT_TOKEN")
        elif not self.chat_id:
            print("  [Telegram] 警告: 未設定 TELEGRAM_CHAT_ID")
        else:
            try:
                self.bot = Bot(token=self.token)
                if self.topic_id:
                    print(f"  [Telegram] Bot 初始化成功 (Topic ID: {self.topic_id})")
                else:
                    print(f"  [Telegram] Bot 初始化成功")
            except Exception as e:
                print(f"  [Telegram] Bot 初始化失敗: {e}")
    
    def _escape_html_special_chars(self, text):
        """
        轉義 HTML 特殊字符，但保留合法的 HTML 標籤
        
        策略：
        1. 先用佔位符替換合法的 HTML 標籤
        2. 轉義所有的 & < >
        3. 還原佔位符為 HTML 標籤
        
        Args:
            text: 包含 HTML 標籤的文字
        
        Returns:
            str: 轉義後的文字
        """
        import re
        import uuid
        
        # 生成唯一佔位符前綴
        placeholder_prefix = f"__HTML_TAG_{uuid.uuid4().hex[:8]}__"
        
        # 儲存合法的 HTML 標籤
        saved_tags = {}
        tag_counter = 0
        
        # Telegram 支援的 HTML 標籤（完整列表）
        # 參考：https://core.telegram.org/bots/api#html-style
        supported_tags = [
            r'<b>(.*?)</b>',
            r'<strong>(.*?)</strong>',
            r'<i>(.*?)</i>',
            r'<em>(.*?)</em>',
            r'<u>(.*?)</u>',
            r'<ins>(.*?)</ins>',
            r'<s>(.*?)</s>',
            r'<strike>(.*?)</strike>',
            r'<del>(.*?)</del>',
            r'<code>(.*?)</code>',
            r'<pre>(.*?)</pre>',
            r'<a\s+href="[^"]*">(.*?)</a>',  # 連結標籤
        ]
        
        # 1. 保存合法的 HTML 標籤
        for pattern in supported_tags:
            def replacer(match):
                nonlocal tag_counter
                placeholder = f"{placeholder_prefix}{tag_counter}{placeholder_prefix}"
                saved_tags[placeholder] = match.group(0)
                tag_counter += 1
                return placeholder
            
            text = re.sub(pattern, replacer, text, flags=re.IGNORECASE | re.DOTALL)
        
        # 2. 轉義特殊字符
        text = text.replace('&', '&amp;')  # & 必須最先處理
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # 3. 還原合法的 HTML 標籤
        for placeholder, original_tag in saved_tags.items():
            text = text.replace(placeholder, original_tag)
        
        return text
    
    def _clean_unsupported_html_tags(self, text):
        """
        清理 Telegram 不支援的 HTML 標籤並轉義特殊字符
        
        Telegram HTML 模式只支援：<b>, <i>, <u>, <s>, <code>, <pre>, <a>
        不支援：<h1>, <h2>, <h3>, <ul>, <ol>, <li>, <p>, <div>, <hr> 等
        
        參考：https://core.telegram.org/bots/api#html-style
        
        Args:
            text: 包含 HTML 標籤的文字
        
        Returns:
            str: 清理並轉義後的文字
        """
        import re
        
        # 第一步：移除不支援的 HTML 標籤
        
        # 1. 移除不支援的標題標籤（h1-h6），保留內容並加粗
        text = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'<b>\1</b>\n', text, flags=re.IGNORECASE)
        
        # 2. 移除列表標籤（ul, ol），保留內容
        text = re.sub(r'</?ul>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?ol>', '', text, flags=re.IGNORECASE)
        
        # 3. 移除列表項目標籤（li），轉換為 "- " 開頭
        text = re.sub(r'<li>(.*?)</li>', r'  - \1\n', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<li>', '  - ', text, flags=re.IGNORECASE)
        
        # 4. 移除段落標籤（p），保留內容並加換行
        text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'</?p>', '', text, flags=re.IGNORECASE)
        
        # 5. 移除水平線標籤（hr），替換為文字分隔線
        text = re.sub(r'<hr\s*/?>', '\n───────────────────\n', text, flags=re.IGNORECASE)
        
        # 6. 移除容器標籤（div, span），保留內容
        text = re.sub(r'</?div[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?span[^>]*>', '', text, flags=re.IGNORECASE)
        
        # 第二步：轉義文本中的 HTML 特殊字符（< > &）
        # 但保留合法的 HTML 標籤
        text = self._escape_html_special_chars(text)
        
        return text
    
    def _markdown_to_html(self, text):
        """
        將簡單的 Markdown 格式轉換為 HTML（Telegram 支援）
        
        轉換規則：
        - **粗體** → <b>粗體</b>
        - *斜體* → <i>斜體</i>
        - `代碼` → <code>代碼</code>
        - # 標題 → <b>標題</b>
        - ## 標題 → <b>標題</b>
        - [文字](連結) → <a href="連結">文字</a>
        
        參考：https://tgtw.cc/post-about-parse-mode-of-telegram
        
        Args:
            text: Markdown 文字
        
        Returns:
            str: HTML 文字
        """
        import re
        
        # 1. 處理標題（# ## ### 開頭的行）
        text = re.sub(r'^###\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^#\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # 2. 處理粗體 **文字**
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # 3. 處理斜體 *文字* （但要避免影響到 ** 的處理）
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        
        # 4. 處理行內代碼 `代碼`
        text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)
        
        # 5. 處理連結 [文字](網址)
        text = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'<a href="\2">\1</a>', text)
        
        # 6. 轉義 HTML 特殊字元（但保留我們剛轉換的 HTML 標籤）
        # 注意：這裡我們不做額外的 HTML 轉義，因為 Telegram 會自動處理
        
        return text
    
    def _add_report_header(self, report_text):
        """
        在報告開頭添加標題和日期
        
        Args:
            report_text: LLM 生成的報告內容
        
        Returns:
            str: 添加標題後的完整報告
        """
        from datetime import datetime
        
        # 獲取當前日期和星期
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
        
        # 組裝報告頭部
        header = f"""<b>📊 專業技術分析日報</b>

<b>報告日期</b>：{current_date} ({weekday_cn})
<b>分析師</b>：系統技術分析師

───────────────────

"""
        
        return header + report_text
    
    def send_report(self, report_text):
        """
        推送報告到 Telegram（同步包裝）
        
        Args:
            report_text: 報告內容 (HTML 格式，LLM 已生成)
        
        Returns:
            bool: 是否發送成功
        """
        if not report_text:
            print("  [Telegram] 報告內容為空，取消推送")
            return False
        
        if not self.bot:
            print("  [Telegram] Bot 未初始化，無法推送")
            return False
        
        # 添加報告頭部（標題和日期）
        report_with_header = self._add_report_header(report_text)
        
        # 清理 LLM 可能生成的不支援 HTML 標籤
        cleaned_text = self._clean_unsupported_html_tags(report_with_header)
        
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
            
            result = loop.run_until_complete(self._send_message_async(cleaned_text))
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
                # 如果設定了 topic_id，則發送到指定的 topic
                send_params = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": ParseMode.HTML,
                    "disable_web_page_preview": True
                }
                
                # 加入 topic ID（如果有設定）
                if self.topic_id:
                    send_params["message_thread_id"] = int(self.topic_id)
                
                message = await self.bot.send_message(**send_params)
                
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
            send_params = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": None,  # 純文字模式
                "disable_web_page_preview": True
            }
            
            # 加入 topic ID（如果有設定）
            if self.topic_id:
                send_params["message_thread_id"] = int(self.topic_id)
            
            message = await self.bot.send_message(**send_params)
            
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
🤖 <b>Telegram Bot 測試訊息</b>

這是一條測試訊息，用於驗證 Bot 連接。

<b>測試項目</b>:
- ✅ HTML 格式
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
    
    async def _get_updates_async(self):
        """
        異步獲取 Bot 的更新訊息（用於查找 Topic ID）
        
        Returns:
            list: 更新訊息列表
        """
        try:
            updates = await self.bot.get_updates(limit=10)
            return updates
        except Exception as e:
            print(f"  [Telegram] 獲取更新失敗: {e}")
            return []
    
    def get_topic_info(self):
        """
        獲取並顯示最近訊息的 Topic ID（用於設定 TELEGRAM_TOPIC_ID）
        
        使用方法：
        1. 在 Telegram 群組的目標 topic 中發送一則訊息（例如：/start）
        2. 執行此函數
        3. 查看輸出中的 message_thread_id
        
        Returns:
            bool: 是否成功獲取資訊
        """
        if not self.bot:
            print("  [Telegram] Bot 未初始化")
            return False
        
        print("\n" + "="*80)
        print("  獲取 Telegram Topic ID")
        print("="*80)
        print("\n請確認你已在目標 Topic 中發送訊息給 Bot（例如：/start）\n")
        
        try:
            # 嘗試獲取現有事件循環
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            updates = loop.run_until_complete(self._get_updates_async())
            
            if not updates:
                print("⚠️  未找到任何更新訊息")
                print("   請先在 Telegram 群組的目標 topic 中發送訊息給 Bot")
                return False
            
            print(f"找到 {len(updates)} 則最近的訊息:\n")
            
            for idx, update in enumerate(updates, 1):
                if update.message:
                    msg = update.message
                    chat_id = msg.chat.id
                    chat_type = msg.chat.type
                    chat_title = msg.chat.title if msg.chat.title else "私人對話"
                    message_thread_id = msg.message_thread_id if hasattr(msg, 'message_thread_id') else None
                    
                    print(f"訊息 #{idx}:")
                    print(f"  Chat ID: {chat_id}")
                    print(f"  Chat 類型: {chat_type}")
                    print(f"  Chat 名稱: {chat_title}")
                    
                    if message_thread_id:
                        print(f"  ✅ Topic ID: {message_thread_id}")
                        print(f"     將以下內容加入 .env 檔案:")
                        print(f"     TELEGRAM_TOPIC_ID={message_thread_id}")
                    else:
                        print(f"  ℹ️  此訊息沒有 Topic ID（可能是主頻道或私人對話）")
                    
                    print()
            
            return True
            
        except Exception as e:
            print(f"  [Telegram] 獲取 Topic 資訊失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
