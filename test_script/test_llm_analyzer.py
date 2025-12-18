# -*- coding: utf-8 -*-
"""
LLM Analyzer 整合測試
測試項目：
1. Gemini API 連接
2. Prompt 組裝
3. 報告生成
4. 格式驗證
5. 備用報告機制
"""

import sys
sys.path.insert(0, '.')

from investment_bot.services.llm_analyzer import LLMAnalyzerService
from investment_bot.config import Config

def print_separator(title=""):
    """印出分隔線"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
    else:
        print('-'*80)

def create_test_data():
    """建立測試數據（使用市場 API 測試的真實數據結構）"""
    
    portfolio_summary = {
        "total_value": 54233.50,
        "assets": [
            {
                "symbol": "TSLA",
                "type": "Stock",
                "qty": 10,
                "current_price": 446.89,
                "market_value": 4468.90,
                "cost_basis": 200.00,
                "unrealized_pl": 2468.90,
                "return_rate": 1.234
            },
            {
                "symbol": "NVDA",
                "type": "Stock",
                "qty": 50,
                "current_price": 180.93,
                "market_value": 9046.50,
                "cost_basis": 150.00,
                "unrealized_pl": 1546.50,
                "return_rate": 0.206
            },
            {
                "symbol": "BTC",
                "type": "Crypto",
                "qty": 0.5,
                "current_price": 87874.79,
                "market_value": 43937.40,
                "cost_basis": 65000.00,
                "unrealized_pl": 11437.40,
                "return_rate": 0.352
            }
        ]
    }
    
    tech_signals = {
        "TSLA": {
            "current_price": 446.89,
            "rsi": 65.43,
            "is_overbought": False,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {"fast": 440.21, "mid": 420.15, "slow": 390.50},
            "macd": {"line": 5.23, "signal": 3.45, "hist": 1.78},
            "bb": {"upper": 480.50, "lower": 410.30, "pct_b": 0.65}
        },
        "NVDA": {
            "current_price": 180.93,
            "rsi": 58.21,
            "is_overbought": False,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {"fast": 178.50, "mid": 165.30, "slow": 150.20},
            "macd": {"line": 2.15, "signal": 1.80, "hist": 0.35},
            "bb": {"upper": 195.00, "lower": 165.00, "pct_b": 0.53}
        },
        "BTC": {
            "current_price": 87874.79,
            "rsi": 78.50,
            "is_overbought": True,
            "is_oversold": False,
            "trend": "Bullish",
            "ema_values": {"fast": 86500.00, "mid": 82000.00, "slow": 75000.00},
            "macd": {"line": 3500.00, "signal": 3200.00, "hist": 300.00},
            "bb": {"upper": 92000.00, "lower": 78000.00, "pct_b": 0.87}
        }
    }
    
    market_sentiment = {
        "value": 16,
        "classification": "Extreme Fear"
    }
    
    return portfolio_summary, tech_signals, market_sentiment

def test_api_configuration():
    """測試 API 配置"""
    print_separator("[1/5] 測試 API 配置")
    
    print("\n  檢查環境變數...")
    
    if Config.GEMINI_API_KEY:
        # 隱藏部分 API Key
        masked_key = Config.GEMINI_API_KEY[:10] + "..." + Config.GEMINI_API_KEY[-4:]
        print(f"    ✅ GEMINI_API_KEY: {masked_key}")
    else:
        print(f"    ❌ GEMINI_API_KEY: 未設定")
        print(f"    ⚠️  請在 .env 中設定 GEMINI_API_KEY")
        return False
    
    print(f"    ✅ GEMINI_MODEL: {Config.GEMINI_MODEL}")
    print(f"    ✅ GEMINI_MAX_RETRIES: {Config.GEMINI_MAX_RETRIES}")
    print(f"    ✅ GEMINI_TEMPERATURE: {Config.GEMINI_TEMPERATURE}")
    print(f"    ✅ GEMINI_MAX_OUTPUT_TOKENS: {Config.GEMINI_MAX_OUTPUT_TOKENS}")
    
    return True

def test_service_initialization():
    """測試服務初始化"""
    print_separator("[2/5] 測試服務初始化")
    
    print("\n  正在初始化 LLMAnalyzerService...")
    
    try:
        service = LLMAnalyzerService()
        
        if service.client:
            print(f"    ✅ Gemini 客戶端初始化成功")
            print(f"    ✅ 模型: {service.model_name}")
            print(f"    ✅ 最大重試次數: {service.max_retries}")
            return service
        else:
            print(f"    ❌ Gemini 客戶端初始化失敗（可能缺少 API Key）")
            return None
            
    except Exception as e:
        print(f"    ❌ 初始化錯誤: {e}")
        return None

def test_prompt_assembly(service):
    """測試 Prompt 組裝"""
    print_separator("[3/5] 測試 Prompt 組裝")
    
    print("\n  正在組裝測試數據...")
    portfolio_summary, tech_signals, market_sentiment = create_test_data()
    
    print(f"    ✅ 持倉數量: {len(portfolio_summary['assets'])} 個")
    print(f"    ✅ 技術分析: {len(tech_signals)} 個標的")
    print(f"    ✅ 市場情緒: {market_sentiment['classification']}")
    
    print("\n  正在組裝 Prompt...")
    try:
        prompt = service._build_prompt(portfolio_summary, tech_signals, market_sentiment)
        
        print(f"    ✅ Prompt 組裝成功")
        print(f"    ✅ 長度: {len(prompt)} 字元")
        print(f"    ✅ 估算 Token: ~{len(prompt) // 3} tokens")
        
        # 檢查關鍵區塊
        required_sections = ['系統角色', '投資組合數據', '技術分析指標', '市場情緒', '報告要求']
        missing_sections = [s for s in required_sections if s not in prompt]
        
        if not missing_sections:
            print(f"    ✅ 所有必要區塊都存在")
        else:
            print(f"    ⚠️  缺少區塊: {missing_sections}")
        
        return portfolio_summary, tech_signals, market_sentiment
        
    except Exception as e:
        print(f"    ❌ Prompt 組裝失敗: {e}")
        return None, None, None

def test_report_generation(service, portfolio_summary, tech_signals, market_sentiment):
    """測試報告生成"""
    print_separator("[4/5] 測試報告生成")
    
    if not portfolio_summary:
        print("\n    ⚠️  跳過測試（前置測試失敗）")
        return None
    
    print("\n  正在呼叫 Gemini API 生成報告...")
    print("  ⏳ 這可能需要 10-30 秒，請稍候...\n")
    
    try:
        report = service.generate_report(portfolio_summary, tech_signals, market_sentiment)
        
        if report:
            print(f"    ✅ 報告生成成功")
            print(f"    ✅ 報告長度: {len(report)} 字元")
            print(f"    ✅ 報告行數: {len(report.split(chr(10)))} 行")
            
            # 檢查是否為備用報告
            if "簡易版" in report or "備用報告" in report:
                print(f"    ⚠️  使用了備用報告（API 可能失敗）")
            else:
                print(f"    ✅ 使用 LLM 生成的完整報告")
            
            return report
        else:
            print(f"    ❌ 報告生成失敗（返回 None）")
            return None
            
    except Exception as e:
        print(f"    ❌ 報告生成錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_report_validation(report):
    """測試報告格式驗證"""
    print_separator("[5/5] 測試報告格式驗證")
    
    if not report:
        print("\n    ⚠️  跳過測試（報告不存在）")
        return False
    
    print("\n  正在驗證報告格式...")
    
    # 檢查基本結構
    checks = {
        "包含標題": "#" in report,
        "包含投資組合": "投資組合" in report or "總覽" in report,
        "包含風險": "風險" in report or "警示" in report,
        "包含建議": "建議" in report or "操作" in report,
        "包含市場情緒": "市場" in report or "情緒" in report or "Fear" in report,
        "使用 Markdown": "##" in report or "###" in report,
        "長度合理": 500 < len(report) < 10000
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"    {status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n    ✅ 所有格式檢查通過")
    else:
        print("\n    ⚠️  部分格式檢查未通過（可能是備用報告）")
    
    return all_passed

def display_report(report):
    """顯示完整報告"""
    print_separator("生成的完整報告")
    
    if report:
        print("\n" + report + "\n")
    else:
        print("\n    ⚠️  無報告內容\n")
    
    print_separator("報告結束")

def main():
    """主測試流程"""
    print("="*80)
    print("  LLM Analyzer 整合測試")
    print("  測試 Gemini API 調用與報告生成")
    print("="*80)
    
    # 測試 1: API 配置
    if not test_api_configuration():
        print("\n❌ 測試終止：API 配置不完整")
        print("請確認 .env 中已設定 GEMINI_API_KEY")
        return
    
    # 測試 2: 服務初始化
    service = test_service_initialization()
    if not service:
        print("\n❌ 測試終止：服務初始化失敗")
        return
    
    # 測試 3: Prompt 組裝
    portfolio_summary, tech_signals, market_sentiment = test_prompt_assembly(service)
    if not portfolio_summary:
        print("\n❌ 測試終止：Prompt 組裝失敗")
        return
    
    # 測試 4: 報告生成
    report = test_report_generation(service, portfolio_summary, tech_signals, market_sentiment)
    
    # 測試 5: 格式驗證
    validation_passed = test_report_validation(report)
    
    # 顯示完整報告
    if report:
        display_report(report)
    
    # 總結
    print_separator("測試總結")
    
    print("\n  📊 測試結果:")
    print(f"    ✅ API 配置: 通過")
    print(f"    ✅ 服務初始化: 通過")
    print(f"    ✅ Prompt 組裝: 通過")
    print(f"    {'✅' if report else '❌'} 報告生成: {'通過' if report else '失敗'}")
    print(f"    {'✅' if validation_passed else '⚠️ '} 格式驗證: {'通過' if validation_passed else '部分通過'}")
    
    if report and validation_passed:
        print("\n  🎉 所有測試通過！LLM Analyzer 運作正常")
    elif report:
        print("\n  ⚠️  報告生成成功但格式需要優化")
    else:
        print("\n  ❌ 報告生成失敗，請檢查 API 配置或網路連接")
    
    print("\n" + "="*80)
    print("  測試完成")
    print("="*80)

if __name__ == "__main__":
    main()






