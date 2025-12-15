# -*- coding: utf-8 -*-
"""
LLM 分析服務 (LLM Analyzer Service)
負責整合 Prompt 並呼叫 LLM 生成投資報告
"""

import time
from datetime import datetime
from ..config import Config

class LLMAnalyzerService:
    def __init__(self):
        """初始化 LLM 服務"""
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.max_retries = Config.GEMINI_MAX_RETRIES
        
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
    
    def generate_report(self, portfolio_summary, tech_signals, market_sentiment):
        """
        生成投資報告
        
        Args:
            portfolio_summary: 持倉摘要 (dict)
            tech_signals: 技術分析訊號 (dict of dicts)
            market_sentiment: 市場情緒 (dict)
        
        Returns:
            str: Markdown 格式的報告內容
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
        
        # 格式化技術指標
        tech_signals_text = self._format_tech_signals(tech_signals)
        
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
    
    def _get_system_role(self):
        """定義系統角色"""
        return """# 系統角色

你是一位**專業的技術分析師**，具備以下特質：

1. **客觀中性**：基於技術指標進行分析，不受情緒影響
2. **數據驅動**：所有判斷都有明確的技術依據（RSI、MACD、EMA、布林通道）
3. **風險意識**：會標註潛在風險（超買、趨勢轉弱、背離）
4. **明確建議**：給出清晰的「買入/賣出/持有」建議，並附上具體數量

你的任務是分析投資組合的技術面狀態，並提供可執行的操作建議。"""
    
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
    
    def _format_tech_signals(self, tech_signals):
        """格式化技術指標數據"""
        if not tech_signals:
            return "_目前沒有技術分析數據_\n"
        
        text = ""
        
        for symbol, signals in tech_signals.items():
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
        """定義輸出要求"""
        return """請根據以上數據生成一份**完整的投資日報**，包含以下區塊：

### 📊 1. 投資組合總覽
- 總市值、今日損益（如果有歷史數據）、整體報酬率

### ⚠️ 2. 風險警示
列出需要特別關注的持倉：
- RSI 超買（> 75）的標的
- 趨勢轉弱（價格跌破 EMA）的標的
- MACD 背離或轉弱的標的

### 🎯 3. 操作建議
針對**每個持倉**，給出明確的建議：

**格式範例**：
- **TSLA (特斯拉)**
  - **建議**: 持有
  - **理由**: RSI 65 處於健康區間，MACD 持續多頭排列，價格站穩 EMA20 上方
  - **參考點位**: 支撐 $440 (EMA20)，壓力 $480 (布林上軌)
  - **操作**: 建議繼續持有現有 10 股

- **BTC (比特幣)**
  - **建議**: 適度減碼
  - **理由**: RSI 78 已超買，MACD 柱狀圖開始縮小，價格接近布林上軌
  - **參考點位**: 壓力 $66,000 (布林上軌)，支撐 $60,000 (EMA10)
  - **操作**: 建議減碼 20%（約 0.1 BTC），降低風險暴露

### 🌍 4. 市場情緒分析
- Fear & Greed Index 的解讀
- 與當前持倉技術面的交叉驗證
- 是否符合當前市場氛圍的配置策略

### 📋 5. 今日重點關注
- 列出 3-5 個最需要關注的標的
- 排序依據：風險程度、技術面變化、操作優先級

---

**注意事項**：
1. 所有建議必須有明確的技術依據（引用具體的指標數值）
2. 數量建議要具體（例如：建議減碼 20%，約 5 股）
3. 使用 Markdown 格式，適合 Telegram 顯示
4. 語氣客觀專業，避免誇大或恐慌
5. 報告總長度控制在 2000-3000 字以內"""
    
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
