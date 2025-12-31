# Prompt 模板文件說明

本目錄存放 LLM 分析服務使用的 Prompt 模板文件。

## 📁 文件結構

```
prompts/
├── README.md                  # 本說明文件
├── system_role.txt            # 系統角色定義
└── output_requirements.txt    # 輸出格式要求
```

## 🔧 如何使用

### 修改 Prompt

你可以直接編輯這些 `.txt` 文件來調整 Prompt，**無需修改 Python 代碼**。

**重要**：
- 文件編碼必須為 **UTF-8**（不使用 BOM）
- 修改後重新執行程式即可生效
- 如果文件不存在或讀取失敗，系統會自動使用預設值

### 文件說明

#### `system_role.txt`
定義 LLM 的角色與特質，例如：
- 專業技術分析師
- 客觀中性、數據驅動
- 風險意識、明確建議

#### `output_requirements.txt`
定義報告的輸出格式要求，包含：
- 報告結構（風險警示、操作建議、市場情緒等）
- 格式範例
- HTML 標籤限制
- 特殊字符限制
- 長度控制

## 🧪 測試

執行以下命令測試 Prompt 載入功能：

```bash
# Windows
$env:PYTHONUTF8=1; uv run python test_script/test_prompt_external.py

# macOS/Linux
uv run python test_script/test_prompt_external.py
```

## 💡 提示

1. **備份原始文件**：修改前建議先備份原始文件
2. **測試修改**：修改後建議執行測試腳本確認載入正常
3. **版本控制**：這些文件可以納入 Git 版本控制，方便追蹤變更
4. **編碼注意**：確保編輯器使用 UTF-8 編碼（不使用 BOM）

## 🔄 回退機制

如果外部文件不存在或讀取失敗，系統會自動使用硬編碼在 `llm_analyzer.py` 中的預設值，確保程式正常運作。
