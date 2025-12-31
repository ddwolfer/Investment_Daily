# -*- coding: utf-8 -*-
"""
測試外部 Prompt 文件載入功能
"""

import sys
from pathlib import Path

# 加入專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from investment_bot.services.llm_analyzer import LLMAnalyzerService

def test_prompt_loading():
    """測試 Prompt 文件載入"""
    print("=" * 80)
    print("  測試外部 Prompt 文件載入")
    print("=" * 80)
    print()
    
    # 初始化服務（會自動載入外部 Prompt）
    print("📂 正在初始化 LLM 服務...")
    service = LLMAnalyzerService()
    print()
    
    # 檢查系統角色
    print("🔍 檢查系統角色 Prompt...")
    system_role = service._get_system_role()
    print(f"  ✅ 系統角色長度: {len(system_role)} 字元")
    print(f"  ✅ 前 100 字元預覽:")
    print(f"     {system_role[:100]}...")
    print()
    
    # 檢查輸出要求
    print("🔍 檢查輸出要求 Prompt...")
    output_requirements = service._get_output_requirements()
    print(f"  ✅ 輸出要求長度: {len(output_requirements)} 字元")
    print(f"  ✅ 前 100 字元預覽:")
    print(f"     {output_requirements[:100]}...")
    print()
    
    # 驗證關鍵內容
    print("✅ 驗證關鍵內容...")
    required_keywords = {
        "system_role": ["技術分析師", "客觀中性", "數據驅動", "風險意識"],
        "output_requirements": ["風險警示", "操作建議", "重點分析標的", "HTML 標籤限制"]
    }
    
    all_passed = True
    for prompt_type, keywords in required_keywords.items():
        content = system_role if prompt_type == "system_role" else output_requirements
        missing = [kw for kw in keywords if kw not in content]
        
        if missing:
            print(f"  ❌ {prompt_type} 缺少關鍵字: {missing}")
            all_passed = False
        else:
            print(f"  ✅ {prompt_type} 包含所有關鍵字")
    
    print()
    
    if all_passed:
        print("=" * 80)
        print("  ✅ 所有測試通過！")
        print("=" * 80)
        print()
        print("💡 提示：")
        print("  - 系統角色文件: prompts/system_role.txt")
        print("  - 輸出要求文件: prompts/output_requirements.txt")
        print("  - 你可以直接編輯這些文件來修改 Prompt，無需修改 Python 代碼")
    else:
        print("=" * 80)
        print("  ❌ 部分測試失敗")
        print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    test_prompt_loading()
