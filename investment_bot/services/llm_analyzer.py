# -*- coding: utf-8 -*-
"""
LLM 分析服務 (LLM Analyzer Service)
負責構建 Prompt 並呼叫 LLM 生成投資日報。
"""

import json
import os
from openai import OpenAI
from ..config import Config

class LLMAnalyzerService:
    def __init__(self):
        """初始化 LLM 服務"""
        # 如果沒有設置 Key，這裡會報錯或無法使用，需確保 .env 有設定
        self.api_key = Config.OPENAI_API_KEY
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            print("警告: 未設定 OPENAI_API_KEY，無法生成 LLM 報告。")
            self.client = None

    def generate_report(self, portfolio_summary, tech_signals, market_sentiment):
        """
        生成投資日報
        :param portfolio_summary: 持倉概況 (dict)
        :param tech_signals: 技術指標信號 (dict of dicts)
        :param market_sentiment: 市場情緒 (dict)
        :return: Markdown 格式的報告字串
        """
        if not self.client:
            return "⚠️ 無法生成報告：缺少 OpenAI API Key。"
            
        # 構建 Context JSON
        context_data = {
            "portfolio": portfolio_summary,
            "market_sentiment": market_sentiment,
            "technical_analysis": tech_signals
        }
        
        # 將數據轉為 JSON 字串，並格式化以便 LLM 閱讀
        # 使用 default=str 避免非標準型別 (如 numpy int/float) 導致序列化失敗
        context_json = json.dumps(context_data, indent=2, ensure_ascii=False, default=str)
        
        system_prompt = """
Role: You are a professional Investment Risk Manager ("The Rational Data-Driven Advisor").
Objective: Analyze the user's daily portfolio and technical data to generate a concise, actionable Telegram report.

Tone: Professional, calm, objective, data-first. Avoid FOMO.

Format Structure (Markdown):
1. 💼 **Portfolio Snapshot**: Total value, top winners/losers (24h), cash/asset ratio.
2. 📈 **Market & Technical Pulse**: 
   - Sentiment Score (Fear & Greed).
   - Key Technical Signals: Highlight only significant signals (e.g., RSI > 75, Price crossing EMA). 
   - Specifically analyze BTC, TSLA, and NVDA.
3. 🌍 **Macro & News Context**: Briefly interpret how current macro events (Interest rates, CPI) affect this specific portfolio.
4. ⚠️ **Risk Radar**: Highlight concentrated risks (e.g., "Tech sector exposure > 40%").
5. 🎯 **Actionable Advice**:
   - If Asset is Overbought (RSI > 75): Suggest "Trim/Take Profit".
   - If Asset is Oversold (RSI < 30) AND Trend is Up: Suggest "Buy the Dip".
   - For "Free" assets (BNB, SOL): Suggest holding or staking unless structure breaks.

Language: Traditional Chinese (繁體中文).
Output: Clean Markdown, structured for mobile reading.
"""

        user_prompt = f"""
Here is the latest data for today's report:

```json
{context_json}
```

Please generate the daily investment report based on this data.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM 生成失敗: {e}")
            return f"⚠️ 報告生成失敗: {str(e)}"

