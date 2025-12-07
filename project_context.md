Project Context & Design Philosophy (專案背景與設計理念)

1. 專案背景 (Background)

使用者是一位同時投資「美股 (US Stocks)」與「加密貨幣 (Crypto)」的投資者。
他希望開發一個 Python 自動化機器人，每天早上定期分析他的投資組合，並透過 Telegram 發送一份 AI 撰寫的投資日報。

2. 數據源頭 (Data Source)

核心數據： 使用者維護的一份 Google Sheet。

數據特徵：

分為兩個區塊：美股 (e.g., TSLA, NVDA, IVV) 與 Crypto (e.g., BTC, ETH, SOL)。

包含欄位：Symbol, Qty, Cost, Market Price, Unrealized P/L。

特殊狀況： 部分 Crypto (如 BNB, SOL, WLD) 被標記為 "FREE" (零成本/空投/戰利品)，這類資產的策略重點在於「守成」與「止盈」。

3. 設計參考 (Design Inspiration)

使用者非常喜歡 Bitget 交易所 的投資日報風格。
期望的報告結構：

資產概覽： 總值、佔比、現金水位。

技術面分析： 不只是列出數字，要包含 EMA 均線排列、RSI 強弱、MACD 動能。

宏觀新聞： 聯準會政策、CPI、板塊輪動（需將新聞與持倉做關聯）。

風險提示： 資金費率、多頭擁擠度、過度集中風險。

交易建議： 具體的 Actionable Item (e.g., "RSI > 80，建議分批止盈")。

4. AI 人設與風格 (Persona & Tone)

角色設定： 「理性數據派的風控官 (Rational Risk Manager)」。

風格要求：

拒絕 FOMO： 不要盲目喊單。

數據優先： 先講 RSI/EMA 數據，再講觀點。

保守穩健： 對於獲利豐厚的資產（如 NVDA, BTC），優先建議「移動止盈」保護利潤；對於虧損資產，客觀評估結構是否破壞。

5. 技術指標邏輯 (Technical Logic Strategy)

開發時請遵循以下分析邏輯：

美股 (Trend-following):

使用 EMA (20/60/120) 判斷中長期趨勢。

使用 RSI (14) 與 MACD 判斷背離。

Crypto (Volatile):

使用 EMA (5/10/20) 判斷短線爆發力。

使用 RSI (6) 捕捉極短線超買訊號。

監控「恐懼與貪婪指數」。

6. 開發目標 (Development Goal)

建立一個基於 Python 的系統，模組化處理：
Google Sheets ETL -> Technical Analysis (Ta-lib) -> LLM Report Generation -> Telegram Notification。