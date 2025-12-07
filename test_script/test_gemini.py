# -*- coding: utf-8 -*-
"""
Gemini API 測試腳本
用於驗證 GEMINI_API_KEY 是否正確以及 Google Generative AI SDK 是否運作正常。
"""

import os
import sys

# 嘗試載入專案根目錄，以便讀取 .env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 載入 .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

# 檢查是否安裝了 google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    print("❌ 尚未安裝 google-generativeai 套件。")
    print("請執行: uv add google-generativeai")
    sys.exit(1)

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ 錯誤: 在 .env 檔案中找不到 'GEMINI_API_KEY'。")
        print("請確保你已經將 OPENAI_API_KEY 替換為 GEMINI_API_KEY。")
        return

    print(f"🔑 檢測到 API Key: {api_key[:5]}...{api_key[-5:]}")
    
    print("🔌 正在設定 Gemini (Model: gemini-flash-latest)...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        print("📡 發送測試請求: '你好，請用繁體中文自我介紹。'...")
        response = model.generate_content("你好，請用繁體中文自我介紹。")
        
        print("\n✅ 測試成功！收到回應：")
        print("="*40)
        print(response.text)
        print("="*40)
        
    except Exception as e:
        print(f"\n❌ API 呼叫失敗: {e}")
        print("可能原因：")
        print("1. API Key 無效或過期")
        print("2. 網路連線問題 (VPN/Proxy)")
        print("3. Google AI Studio 服務地區限制")

if __name__ == "__main__":
    test_gemini()

