# -*- coding: utf-8 -*-
"""
Gemini CLI 測試腳本 (Subprocess版)
嘗試直接呼叫系統中的 'gemini' 指令。
"""

import subprocess
import shutil
import os
import sys

def test_gemini_cli():
    print("🔍 正在檢查 'gemini' 指令...")

    # 1. 檢查指令是否存在於 Path 中
    # 注意：在 Windows 上，npm 安裝的指令通常是 gemini.cmd 或 gemini.ps1
    executable = shutil.which("gemini")
    
    if executable:
        print(f"✅ 找到指令: {executable}")
    else:
        print("⚠️ 警告: 系統 Path 中找不到 'gemini'。")
        print("嘗試在當前環境直接執行...")

    # 2. 測試指令 (嘗試傳入簡單參數)
    # 假設 CLI 的用法是: gemini "你的 Prompt"
    prompt = "Hi, are you Google Gemini?"
    
    print(f"🚀 嘗試執行: gemini \"{prompt}\"")
    
    try:
        # shell=True 允許 Python 透過 Shell 解析指令 (有助於找到 npm 的 .cmd 檔)
        # 但要注意這會有安全風險 (Command Injection)，測試用無妨
        result = subprocess.run(
            f'gemini "{prompt}"', 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'  # 確保處理中文輸出
        )
        
        print("\n--- STDOUT (標準輸出) ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- STDERR (錯誤輸出) ---")
            print(result.stderr)
            
        print("\n--- Return Code ---")
        print(result.returncode)

        if result.returncode == 0:
            print("\n✅ CLI 呼叫成功！")
        else:
            print("\n❌ CLI 回傳錯誤代碼。")
            
    except Exception as e:
        print(f"\n❌ Python 執行失敗: {e}")

if __name__ == "__main__":
    test_gemini_cli()

