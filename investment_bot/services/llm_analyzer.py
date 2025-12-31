# -*- coding: utf-8 -*-
"""
LLM 分析服務 (LLM Analyzer Service)
負責整合 Prompt 並呼叫 LLM 生成投資報告
"""

import os
import time
from datetime import datetime
from pathlib import Path
from ..config import Config

class LLMAnalyzerService:
    def __init__(self):
        """初始化 LLM 服務"""
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.max_retries = Config.GEMINI_MAX_RETRIES
        
        # 載入外部 Prompt 文件
        self.prompt_dir = Path(__file__).parent.parent.parent / "prompts"
        self.system_role = self._load_prompt_file("system_role.txt")
        self.output_requirements = self._load_prompt_file("output_requirements.txt")
        
        # 延遲初始化 Gemini（避免沒有 API Key 時報錯）
        self.client = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                print(f"  [LLM] Gemini 服務初始化成功 (模型: {self.model_name})")
            except Exception as e:
                print(f"  [LLM] Gemini 初始化失敗: {e}")
        else:
            print("  [LLM] 警告: 未設定 GEMINI_API_KEY，LLM 功能將無法使用")
    
    def _load_prompt_file(self, filename):
        """
        載入外部 Prompt 文件
        
        Args:
            filename: 文件名（例如：system_role.txt）
        
        Returns:
            str: 文件內容，如果文件不存在則返回預設值
        """
        file_path = self.prompt_dir / filename
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    print(f"  [LLM] 已載入外部 Prompt: {filename}")
                    return content
            else:
                print(f"  [LLM] 警告: Prompt 文件不存在 ({file_path})，使用預設值")
                return self._get_default_prompt(filename)
        except Exception as e:
            print(f"  [LLM] 讀取 Prompt 文件失敗 ({filename}): {e}，使用預設值")
            return self._get_default_prompt(filename)
    
    def _get_default_prompt(self, filename):
        """
        取得預設的 Prompt 內容（當外部文件不存在時使用）
        
        Args:
            filename: 文件名
        
        Returns:
            str: 預設 Prompt 內容
        """
        defaults = {
            "system_role.txt": """# 系統角色

你是一位**專業的技術分析師**，具備以下特質：

1. **客觀中性**：基於技術指標進行分析，不受情緒影響
2. **數據驅動**：所有判斷都有明確的技術依據（RSI、MACD、EMA、布林通道）
3. **風險意識**：會標註潛在風險（超買、趨勢轉弱、背離）
4. **明確建議**：給出清晰的「買入/賣出/持有」建議，並附上具體數量

你的任務是分析投資組合的技術面狀態，並提供可執行的操作建議。""",
            "output_requirements.txt": """請根據以上數據生成一份**分層投資日報**，包含以下區塊：

<b>注意</b>：請直接從「風險警示」開始，不需要生成報告標題、日期或分析師資訊（這些會由系統自動添加）

<b>⚠️ 1. 風險警示</b>
列出需要立即關注的問題：
- RSI 超買/超賣的標的
- 趨勢轉弱的標的
- 價格突破布林通道的標的
- 用 1-2 句話總結整體風險程度

<b>🎯 2. 操作建議（分層報告）</b>

<b>2.1 重點分析標的（詳細）</b>
針對「重點分析標的」區塊中的每個標的，進行<b>詳細分析</b>（每個約 100-150 字）：

<b>格式範例</b>：
- <b>TSLA (特斯拉)</b>
  - <b>建議</b>: 持有
  - <b>理由</b>: RSI 65.43 處於健康區間，MACD 持續多頭排列，價格站穩 EMA20 上方
  - <b>參考點位</b>: 支撐 $440 (EMA20)，壓力 $480 (布林上軌)
  - <b>操作</b>: 建議繼續持有現有 10 股

- <b>BTC (比特幣)</b>
  - <b>建議</b>: 適度減碼
  - <b>理由</b>: RSI 78.50 已超買，價格接近布林上軌 $92,000
  - <b>參考點位</b>: 壓力 $92,000 (布林上軌)，支撐 $86,500 (EMA20)
  - <b>操作</b>: 建議減碼 20%（約 0.1 BTC），降低風險暴露

<b>2.2 其他持倉（摘要）</b>
針對「其他持倉」區塊中的標的，用<b>一行總結</b>（每個約 15-20 字）：

<b>格式範例</b>：
- <b>AAPL</b>: 持有，技術面穩健，RSI 58
- <b>MSFT</b>: 持有，多頭趨勢，無風險訊號
- <b>ETH</b>: 持有，跟隨 BTC 走勢

<b>🌍 3. 市場情緒分析</b>
- Fear & Greed Index 的解讀（1-2 句話）
- 與當前持倉技術面的交叉驗證
- 是否符合當前市場氛圍

<b>📋 4. 今日重點關注</b>
- 列出 2-3 個最需要優先處理的標的
- 一句話說明優先級理由

---

<b>重要：格式要求</b>
1. 重點分析標的：每個 100-150 字，必須有明確技術依據
2. 其他持倉：每個 15-20 字，簡潔總結即可
3. 數量建議要具體（例如：建議減碼 20%，約 5 股）
4. <b>HTML 標籤限制（重要）</b>：
   - <b>只能使用</b>：<b>粗體</b>、<i>斜體</i>、<code>代碼</code>、<pre>預格式化</pre>
   - <b>禁止使用</b>：h1/h2/h3 標題標籤、ul/ol/li 列表標籤、p/div/span 容器、hr 水平線
   - 標題改用 <b>標題文字</b> + 換行
   - 列表改用「- 」或「• 」開頭的純文字
   - 分隔線改用「───」
5. <b>特殊字元限制（非常重要）</b>：
   - <b>絕對禁止</b>使用小於號 < 和大於號 > 符號
   - 比較運算請改用文字：「高於」、「低於」、「大於」、「小於」、「超過」、「不足」
   - 例如：「RSI 低於 30」而非「RSI < 30」
   - 例如：「價格高於 EMA20」而非「價格 > EMA20」
6. 語氣客觀專業，避免誇大或恐慌
7. <b>報告總長度控制在 1500-2200 字以內</b>（重點在質量而非數量）"""
        }
        
        return defaults.get(filename, "")
    
    def generate_report(self, portfolio_summary, tech_signals, market_sentiment):
        """
        生成投資報告
        
        Args:
            portfolio_summary: 持倉摘要 (dict)
            tech_signals: 技術分析訊號 (dict of dicts)
            market_sentiment: 市場情緒 (dict)
        
        Returns:
            str: HTML 格式的報告內容（適合 Telegram 顯示）
        """
        if not self.client:
            print("  [LLM] 錯誤: Gemini 服務未初始化")
            return self._generate_fallback_report(portfolio_summary, tech_signals, market_sentiment)
        
        # 組裝 Prompt
        prompt = self._build_prompt(portfolio_summary, tech_signals, market_sentiment)
        
        # 呼叫 API（帶重試機制）
        try:
            response = self._call_gemini_api(prompt)
            
            # 驗證回應格式
            if response and self._validate_response(response):
                return response
            else:
                print("  [LLM] 警告: 回應格式驗證失敗，使用備用報告")
                return self._generate_fallback_report(portfolio_summary, tech_signals, market_sentiment)
                
        except Exception as e:
            print(f"  [LLM] 錯誤: {e}")
            return self._generate_fallback_report(portfolio_summary, tech_signals, market_sentiment)
    
    def _build_prompt(self, portfolio_summary, tech_signals, market_sentiment):
        """
        組裝完整的 Prompt
        
        Returns:
            str: 完整的提示詞
        """
        # 系統角色定義
        system_role = self._get_system_role()
        
        # 格式化持倉數據
        portfolio_text = self._format_portfolio_data(portfolio_summary)
        
        # 智能篩選重點分析標的
        focus_symbols, summary_symbols = self._select_focus_symbols(portfolio_summary, tech_signals)
        
        # 格式化技術指標（分層輸出）
        tech_signals_text = self._format_tech_signals(tech_signals, focus_symbols, summary_symbols)
        
        # 格式化市場情緒
        sentiment_text = self._format_market_sentiment(market_sentiment)
        
        # 輸出要求
        output_requirements = self._get_output_requirements()
        
        # 組裝完整 Prompt
        prompt = f"""
{system_role}

---

## 📊 投資組合數據

{portfolio_text}

---

## 📈 技術分析指標

{tech_signals_text}

---

## 🌍 市場情緒指數

{sentiment_text}

---

## 📋 報告要求

{output_requirements}

---

請根據以上數據生成完整的投資日報。
"""
        
        return prompt
    
    def _select_focus_symbols(self, portfolio_summary, tech_signals):
        """
        智能篩選需要重點分析的標的
        
        優先級：
        1. Watchlist（手動指定的核心標的）
        2. 風險警示（自動識別有問題的標的）
        3. 限制數量（避免 token 超標）
        
        Args:
            portfolio_summary: 持倉摘要
            tech_signals: 技術分析訊號
        
        Returns:
            tuple: (focus_symbols, summary_symbols)
        """
        focus_symbols = []
        summary_symbols = []
        
        # 獲取跳過清單
        skip_list = getattr(Config, 'ANALYSIS_SKIP_LIST', [])
        
        # 第 1 層：Watchlist（優先）
        for symbol in Config.ANALYSIS_WATCHLIST:
            if symbol in skip_list:
                continue  # 跳過黑名單標的
            if symbol in tech_signals:
                focus_symbols.append(symbol)
                print(f"  [LLM] Watchlist 核心標的: {symbol}")
        
        # 第 2 層：風險警示自動篩選
        for symbol, signals in tech_signals.items():
            if symbol in focus_symbols or symbol in skip_list:
                continue  # 已在 watchlist 中或在跳過清單中
            
            # 檢查風險條件
            risk_reasons = []
            
            if signals.get('is_overbought'):
                risk_reasons.append("RSI 超買")
            
            if signals.get('is_oversold'):
                risk_reasons.append("RSI 超賣")
            
            if signals.get('trend') == 'Bearish':
                risk_reasons.append("趨勢轉弱")
            
            # 檢查布林通道突破
            bb = signals.get('bb', {})
            pct_b = bb.get('pct_b', 0.5)
            if pct_b > 1.0:
                risk_reasons.append("突破布林上軌")
            elif pct_b < 0:
                risk_reasons.append("跌破布林下軌")
            
            if risk_reasons:
                focus_symbols.append(symbol)
                print(f"  [LLM] 風險警示加入重點: {symbol} ({', '.join(risk_reasons)})")
        
        # 限制數量（避免太多）
        if len(focus_symbols) > Config.ANALYSIS_MAX_FOCUS:
            print(f"  [LLM] 重點標的過多 ({len(focus_symbols)} 個)，限制為前 {Config.ANALYSIS_MAX_FOCUS} 個")
            focus_symbols = focus_symbols[:Config.ANALYSIS_MAX_FOCUS]
        
        # 第 3 層：其他標的進入簡要總結
        for symbol in tech_signals.keys():
            if symbol not in focus_symbols and symbol not in skip_list:
                summary_symbols.append(symbol)
        
        print(f"  [LLM] 📊 重點分析標的 ({len(focus_symbols)} 個): {focus_symbols}")
        if summary_symbols:
            print(f"  [LLM] 📝 簡要總結標的 ({len(summary_symbols)} 個): {summary_symbols}")
        
        return focus_symbols, summary_symbols
    
    def _get_system_role(self):
        """取得系統角色定義（從外部文件或預設值）"""
        return self.system_role
    
    def _format_portfolio_data(self, portfolio_summary):
        """格式化持倉數據"""
        total_value = portfolio_summary.get('total_value', 0)
        assets = portfolio_summary.get('assets', [])
        
        text = f"### 投資組合總覽\n\n"
        text += f"- **總市值**: ${total_value:,.2f}\n"
        text += f"- **持倉數量**: {len(assets)} 個標的\n\n"
        
        if not assets:
            text += "_目前沒有持倉數據_\n"
            return text
        
        text += "### 持倉明細\n\n"
        text += "| 標的 | 類型 | 數量 | 成本 | 現價 | 市值 | 損益 | 報酬率 |\n"
        text += "|------|------|------|------|------|------|------|--------|\n"
        
        for asset in assets:
            symbol = asset.get('symbol', 'N/A')
            asset_type = asset.get('type', 'N/A')
            qty = asset.get('qty', 0)
            cost = asset.get('cost_basis', 0)
            price = asset.get('current_price', 0)
            value = asset.get('market_value', 0)
            pl = asset.get('unrealized_pl', 0)
            ret = asset.get('return_rate', 0)
            
            # 格式化報酬率
            ret_str = f"{ret*100:+.2f}%"
            pl_str = f"${pl:+,.2f}"
            
            text += f"| {symbol} | {asset_type} | {qty:.2f} | ${cost:.2f} | ${price:.2f} | ${value:,.2f} | {pl_str} | {ret_str} |\n"
        
        return text
    
    def _format_tech_signals(self, tech_signals, focus_symbols, summary_symbols):
        """
        格式化技術指標數據（分層輸出）
        
        Args:
            tech_signals: 所有技術分析數據
            focus_symbols: 需要詳細分析的標的列表
            summary_symbols: 只需簡要總結的標的列表
        """
        if not tech_signals:
            return "_目前沒有技術分析數據_\n"
        
        text = ""
        
        # === 第 1 部分：重點標的（詳細分析） ===
        if focus_symbols:
            text += "### 🎯 重點分析標的\n\n"
            text += "_以下標的需要詳細關注（Watchlist + 風險警示）_\n\n"
        
        for symbol in focus_symbols:
            if symbol not in tech_signals:
                continue
            
            signals = tech_signals[symbol]
            text += f"### {symbol}\n\n"
            
            # 基本資訊
            current_price = signals.get('current_price', 0)
            trend = signals.get('trend', 'N/A')
            text += f"- **現價**: ${current_price:.2f}\n"
            text += f"- **趨勢**: {trend} {'📈' if trend == 'Bullish' else '📉'}\n\n"
            
            # RSI
            rsi = signals.get('rsi', 0)
            is_overbought = signals.get('is_overbought', False)
            is_oversold = signals.get('is_oversold', False)
            
            rsi_status = ""
            if is_overbought:
                rsi_status = " ⚠️ **超買**"
            elif is_oversold:
                rsi_status = " 💡 **超賣**"
            
            text += f"**RSI**: {rsi:.2f}{rsi_status}\n\n"
            
            # EMA
            ema_values = signals.get('ema_values', {})
            text += f"**EMA 排列**:\n"
            text += f"- 快線 (EMA20): ${ema_values.get('fast', 0):.2f}\n"
            text += f"- 中線 (EMA60): ${ema_values.get('mid', 0):.2f}\n"
            text += f"- 慢線 (EMA120): ${ema_values.get('slow', 0):.2f}\n\n"
            
            # MACD
            macd = signals.get('macd', {})
            macd_line = macd.get('line', 0)
            macd_signal = macd.get('signal', 0)
            macd_hist = macd.get('hist', 0)
            
            macd_trend = "多頭" if macd_hist > 0 else "空頭"
            text += f"**MACD**: {macd_trend}\n"
            text += f"- MACD Line: {macd_line:.2f}\n"
            text += f"- Signal Line: {macd_signal:.2f}\n"
            text += f"- Histogram: {macd_hist:.2f}\n\n"
            
            # 布林通道
            bb = signals.get('bb', {})
            bb_upper = bb.get('upper', 0)
            bb_lower = bb.get('lower', 0)
            bb_pct_b = bb.get('pct_b', 0)
            
            text += f"**布林通道**:\n"
            text += f"- 上軌: ${bb_upper:.2f}\n"
            text += f"- 下軌: ${bb_lower:.2f}\n"
            text += f"- %B 位置: {bb_pct_b:.2f} "
            
            if bb_pct_b > 1:
                text += "（價格突破上軌）\n"
            elif bb_pct_b < 0:
                text += "（價格跌破下軌）\n"
            elif bb_pct_b > 0.8:
                text += "（接近上軌）\n"
            elif bb_pct_b < 0.2:
                text += "（接近下軌）\n"
            else:
                text += "（位於通道內）\n"
            
            text += "\n---\n\n"
        
        # === 第 2 部分：其他持倉（簡要總結） ===
        if summary_symbols:
            text += "### 📝 其他持倉（簡要總結）\n\n"
            text += "_以下標的技術面穩定，僅做簡要記錄_\n\n"
            
            for symbol in summary_symbols:
                if symbol not in tech_signals:
                    continue
                
                signals = tech_signals[symbol]
                current_price = signals.get('current_price', 0)
                trend = signals.get('trend', 'N/A')
                rsi = signals.get('rsi', 0)
                
                # 一行總結
                trend_emoji = "📈" if trend == "Bullish" else "📉"
                text += f"- **{symbol}**: ${current_price:.2f}, {trend} {trend_emoji}, RSI {rsi:.0f}\n"
            
            text += "\n"
        
        return text
    
    def _format_market_sentiment(self, market_sentiment):
        """格式化市場情緒數據"""
        if not market_sentiment:
            return "_市場情緒數據不可用_\n"
        
        value = market_sentiment.get('value', 50)
        classification = market_sentiment.get('classification', 'Neutral')
        
        # 情緒描述
        emoji = "😱" if value < 25 else "😰" if value < 45 else "😐" if value < 55 else "😊" if value < 75 else "🤑"
        
        text = f"### Fear & Greed Index\n\n"
        text += f"- **指數值**: {value} / 100 {emoji}\n"
        text += f"- **分類**: {classification}\n\n"
        
        # 解讀
        if value < 25:
            interpretation = "市場處於**極度恐慌**狀態，可能是逢低佈局的機會，但需注意是否有基本面惡化的因素。"
        elif value < 45:
            interpretation = "市場**恐慌**情緒明顯，投資人風險偏好降低，適合觀察是否有超跌反彈機會。"
        elif value < 55:
            interpretation = "市場情緒**中性**，觀望氣氛濃厚，建議依據個股技術面進行操作。"
        elif value < 75:
            interpretation = "市場**貪婪**情緒升溫，資金積極進場，但需留意是否過熱。"
        else:
            interpretation = "市場處於**極度貪婪**狀態，警惕泡沫風險，建議適度獲利了結。"
        
        text += f"**解讀**: {interpretation}\n"
        
        return text
    
    def _get_output_requirements(self):
        """取得輸出要求（從外部文件或預設值）"""
        return self.output_requirements
    
    def _call_gemini_api(self, prompt):
        """
        呼叫 Gemini API（帶重試機制）
        
        Args:
            prompt: 完整的提示詞
        
        Returns:
            str: LLM 回應內容
        """
        for attempt in range(self.max_retries):
            try:
                print(f"  [LLM] 正在呼叫 Gemini API (嘗試 {attempt + 1}/{self.max_retries})...")
                
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        'temperature': Config.GEMINI_TEMPERATURE,
                        'max_output_tokens': Config.GEMINI_MAX_OUTPUT_TOKENS,
                    }
                )
                
                if response and response.text:
                    print(f"  [LLM] API 調用成功，回應長度: {len(response.text)} 字元")
                    return response.text
                else:
                    print(f"  [LLM] 警告: API 回應為空")
                    
            except Exception as e:
                print(f"  [LLM] API 調用失敗 (第 {attempt + 1} 次): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"  [LLM] 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"  [LLM] 已達最大重試次數，放棄調用")
                    raise
        
        return None
    
    def _validate_response(self, response):
        """
        驗證 LLM 回應格式
        
        Args:
            response: LLM 回應內容
        
        Returns:
            bool: 是否有效
        """
        if not response or len(response) < 100:
            return False
        
        # 簡單檢查是否包含關鍵區塊
        required_keywords = ['投資組合', '風險', '建議', '市場']
        
        for keyword in required_keywords:
            if keyword not in response:
                print(f"  [LLM] 驗證失敗: 缺少關鍵字 '{keyword}'")
                return False
        
        return True
    
    def _generate_fallback_report(self, portfolio_summary, tech_signals, market_sentiment):
        """
        生成備用報告（當 LLM 不可用時）
        
        Returns:
            str: 基本的技術摘要
        """
        print("  [LLM] 使用備用報告模式...")
        
        report = f"# 📊 投資日報（簡易版）\n\n"
        report += f"_由於 LLM 服務不可用，以下為基本技術摘要_\n\n"
        report += f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        # 投資組合總覽
        total_value = portfolio_summary.get('total_value', 0)
        assets = portfolio_summary.get('assets', [])
        
        report += f"## 💰 投資組合總覽\n\n"
        report += f"- 總市值: ${total_value:,.2f}\n"
        report += f"- 持倉數量: {len(assets)} 個標的\n\n"
        
        # 技術指標摘要
        if tech_signals:
            report += "## 📈 技術指標摘要\n\n"
            
            for symbol, signals in tech_signals.items():
                trend = signals.get('trend', 'N/A')
                rsi = signals.get('rsi', 0)
                is_overbought = signals.get('is_overbought', False)
                is_oversold = signals.get('is_oversold', False)
                
                report += f"**{symbol}**: {trend} | RSI {rsi:.2f}"
                
                if is_overbought:
                    report += " ⚠️ 超買"
                elif is_oversold:
                    report += " 💡 超賣"
                
                report += "\n"
            
            report += "\n"
        
        # 市場情緒
        if market_sentiment:
            value = market_sentiment.get('value', 50)
            classification = market_sentiment.get('classification', 'Neutral')
            report += f"## 🌍 市場情緒\n\n"
            report += f"Fear & Greed Index: {value} ({classification})\n\n"
        
        report += "---\n\n"
        report += "_完整分析報告需要啟用 Gemini API_\n"
        
        return report
