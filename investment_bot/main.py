# -*- coding: utf-8 -*-
"""
主程式入口 (Main Entry Point)
負責協調各個服務模組，執行每日投資日報生成與發送流程。
"""

import sys
import os

# Add the project root to sys.path to ensure imports work correctly
# Assuming structure: project_root/investment_bot/main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from investment_bot.services.google_sheet import GoogleSheetService
    from investment_bot.services.market_data import MarketDataService
    from investment_bot.services.tech_analysis import TechnicalAnalysisService
    from investment_bot.services.llm_analyzer import LLMAnalyzerService
    from investment_bot.services.telegram_bot import TelegramBotService
except ImportError as e:
    print(f"Import Error: {e}")
    print("請嘗試在專案根目錄執行: python -m investment_bot.main")
    sys.exit(1)

def main():
    print("🚀 啟動 AI 投資日報機器人...")
    
    # 1. 初始化服務
    print("🔧 初始化服務中...")
    try:
        sheet_service = GoogleSheetService()
        market_service = MarketDataService()
        ta_service = TechnicalAnalysisService()
        llm_service = LLMAnalyzerService()
        telegram_service = TelegramBotService()
    except Exception as e:
        print(f"❌ 服務初始化失敗: {e}")
        return

    # 2. 獲取持倉數據
    print("📊 正在讀取 Google Sheet 持倉數據...")
    portfolio_df = sheet_service.get_portfolio_data()
    
    if portfolio_df.empty:
        print("⚠️ 持倉數據為空，將嘗試使用 Mock 數據或停止...")
        # 在 get_portfolio_data 內部已經處理了 Mock 邏輯，如果這裡還是空，那就是真的空了
        if portfolio_df.empty:
             print("❌ 無法獲取有效數據，程式終止。")
             return

    # 3. 準備數據容器
    tech_signals = {}
    portfolio_summary = {
        "total_value": 0,
        "assets": []
    }
    
    # 4. 遍歷每個持倉，獲取市場數據並計算指標
    print("📉 正在進行技術分析 (這可能需要一點時間)...")
    total_value = 0
    
    for _, row in portfolio_df.iterrows():
        symbol = row['Symbol']
        asset_type = row['Type']
        qty = row['Qty']
        cost = row['Cost']
        
        print(f"  -> 處理中: {symbol} ({asset_type})...")
        
        # 抓取歷史數據
        hist_df = market_service.get_historical_data(symbol, asset_type)
        
        if not hist_df.empty:
            # 進行技術分析
            analysis = ta_service.analyze(hist_df, asset_type)
            
            if analysis:
                tech_signals[symbol] = analysis
                # 更新最新價格與市值
                current_price = analysis['current_price']
                market_value = current_price * qty
                total_value += market_value
                
                # 計算損益
                # 如果 cost 為 0 (Free tokens)，unrealized_pl 就是 market_value
                unrealized_pl = market_value - (cost * qty)
                return_rate = (unrealized_pl / (cost * qty)) if cost > 0 else 0
                
                # 更新持倉資訊
                portfolio_summary['assets'].append({
                    "symbol": symbol,
                    "type": asset_type,
                    "qty": qty,
                    "current_price": current_price,
                    "market_value": market_value,
                    "cost_basis": cost,
                    "unrealized_pl": unrealized_pl,
                    "return_rate": return_rate
                })
            else:
                print(f"     ⚠️ 技術分析失敗: {symbol} (數據不足)")
        else:
            print(f"     ⚠️ 無法獲取歷史數據: {symbol}")

    portfolio_summary['total_value'] = total_value
    print(f"💰 投資組合總價值: ${total_value:,.2f}")
    
    # 5. 獲取市場情緒
    print("😨 正在獲取恐懼貪婪指數...")
    sentiment = market_service.get_fear_and_greed_index()
    print(f"   指數: {sentiment['value']} ({sentiment['classification']})")
    
    # 6. 生成報告
    print("🧠 正在呼叫 LLM 生成報告 (請稍候)...")
    report = llm_service.generate_report(portfolio_summary, tech_signals, sentiment)
    
    # 7. 發送報告
    print("📨 正在發送 Telegram 通知...")
    telegram_service.send_report(report)
    
    print("✅ 任務完成！")

if __name__ == "__main__":
    main()

