# -*- coding: utf-8 -*-
"""
LLM ???? (LLM Analyzer Service)
鞎痊瑽遣 Prompt 銝血??LLM ?????亙??
"""

import json
import os
from openai import OpenAI
from ..config import Config

class LLMAnalyzerService:
    def __init__(self):
        """????LLM ??"""
        # 憒?瘝?閮剔蔭 Key嚗ㄐ??舀??⊥?雿輻嚗?蝣箔? .env ?身摰?
        self.api_key = Config.OPENAI_API_KEY
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            print("霅血?: ?芾身摰?OPENAI_API_KEY嚗瘜???LLM ?勗???)
            self.client = None

    def generate_report(self, portfolio_summary, tech_signals, market_sentiment):
        """
        ?????亙
        :param portfolio_summary: ??瘜?(dict)
        :param tech_signals: ?銵?璅縑??(dict of dicts)
        :param market_sentiment: 撣?? (dict)
        :return: Markdown ?澆????銝?
        """
        if not self.client:
            return "?? ?⊥????勗?嚗撩撠?OpenAI API Key??
            
        # 瑽遣 Context JSON
        context_data = {
            "portfolio": portfolio_summary,
            "market_sentiment": market_sentiment,
            "technical_analysis": tech_signals
        }
        
        # 撠????JSON 摮葡嚗蒂?澆??誑靘?LLM ?梯?
        # 雿輻 default=str ?踹???皞???(憒?numpy int/float) 撠摨??仃??
        context_json = json.dumps(context_data, indent=2, ensure_ascii=False, default=str)
        
        system_prompt = """
Role: You are a professional Investment Risk Manager ("The Rational Data-Driven Advisor").
Objective: Analyze the user's daily portfolio and technical data to generate a concise, actionable Telegram report.

Tone: Professional, calm, objective, data-first. Avoid FOMO.

Format Structure (Markdown):
1. ? **Portfolio Snapshot**: Total value, top winners/losers (24h), cash/asset ratio.
2. ?? **Market & Technical Pulse**: 
   - Sentiment Score (Fear & Greed).
   - Key Technical Signals: Highlight only significant signals (e.g., RSI > 75, Price crossing EMA). 
   - Specifically analyze BTC, TSLA, and NVDA.
3. ?? **Macro & News Context**: Briefly interpret how current macro events (Interest rates, CPI) affect this specific portfolio.
4. ?? **Risk Radar**: Highlight concentrated risks (e.g., "Tech sector exposure > 40%").
5. ? **Actionable Advice**:
   - If Asset is Overbought (RSI > 75): Suggest "Trim/Take Profit".
   - If Asset is Oversold (RSI < 30) AND Trend is Up: Suggest "Buy the Dip".
   - For "Free" assets (BNB, SOL): Suggest holding or staking unless structure breaks.

Language: Traditional Chinese (蝜?銝剜?).
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
            print(f"LLM ??憭望?: {e}")
            return f"?? ?勗???憭望?: {str(e)}"

