# 錯誤日誌 (Error Log) & 學習筆記

這份文件記錄了專案開發過程中的技術障礙、錯誤訊息、根本原因分析 (Root Cause Analysis) 以及解決方案。目標是累積知識庫，不僅是解決問題，更要理解「為什麼」會發生以及「為什麼」這樣修有效。

## 📅 2025-12-07

### 1. `uv sync` 編碼錯誤 (UnicodeDecodeError)

*   **錯誤訊息 (Error Message)**:
    ```text
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
    ```
    發生在 `uv sync` 嘗試讀取 `README.md` 時。

*   **根本原因 (Root Cause)**:
    *   Windows PowerShell 在使用 `>` 重導向建立檔案時，預設使用 **UTF-16 LE (Little Endian)** 編碼，並帶有 BOM (Byte Order Mark, `0xff 0xfe`)。
    *   `uv` (以及大多數現代 Linux/Python 工具) 預期文字檔案是標準的 **UTF-8** 編碼（無 BOM）。
    *   當 `uv` 嘗試用 utf-8 解碼器讀取以 `0xff` 開頭的檔案時，就會直接崩潰。

*   **解決方案 (Solution)**:
    *   使用 PowerShell 強制將檔案轉存為 UTF-8。
    *   指令：`$content = Get-Content README.md; $content | Out-File -FilePath README.md -Encoding utf8`
    *   *學習點*：在 Windows 環境下用腳本產生檔案給跨平台工具使用時，務必注意編碼問題。

### 2. `hatchling` 建置失敗 (Package Discovery Failed)

*   **錯誤訊息 (Error Message)**:
    ```text
    ValueError: Unable to determine which files to ship inside the wheel using the following heuristics: ...
    The most likely cause of this is that there is no directory that matches the name of your project (investment_daily).
    ```

*   **根本原因 (Root Cause)**:
    *   我們使用 `hatchling` 作為 build backend。
    *   在 `pyproject.toml` 中，專案名稱定義為 `investment-daily`。
    *   `hatchling` 的預設行為是去尋找與專案名稱一致的資料夾 (即 `investment_daily` 或 `src/investment_daily`)。
    *   但我們的程式碼實際存放於 `investment_bot` 資料夾，導致自動偵測失敗。

*   **解決方案 (Solution)**:
    *   在 `pyproject.toml` 中明確指定 source package 的位置。
    *   配置：
        ```toml
        [tool.hatch.build.targets.wheel]
        packages = ["investment_bot"]
        ```
    *   *學習點*：Python 的打包工具雖然越來越聰明，但當「專案名稱」與「套件名稱」不一致時，必須顯式設定 mapping。

### 3. 冗餘的邏輯檢查 (Redundant Logic Check)

*   **錯誤訊息 (Error Message)**:
    代碼邏輯錯誤（非 Runtime Error）：在 `main.py` 中進行了無意義的嵌套檢查。
    ```python
    if portfolio_df.empty:
        # ...
        if portfolio_df.empty:  # Unreachable logic
            return
    ```

*   **根本原因 (Root Cause)**:
    *   開發時的邏輯混淆。誤以為在第一個 `if` 區塊內 `portfolio_df` 有機會被重新賦值（例如嘗試第二次獲取數據），但實際上並沒有相關代碼。
    *   `get_portfolio_data` 函數內部已經處理了 Mock Data 的 fallback 機制，因此當它返回空值時，代表所有嘗試都已失敗。

*   **解決方案 (Solution)**:
    *   刪除內部冗餘的 `if` 檢查，簡化為單一的錯誤退出邏輯。

### 4. 潛在的除以零錯誤 (Potential Division by Zero)

*   **錯誤訊息 (Error Message)**:
    代碼邏輯隱患：計算回報率時僅檢查 `cost > 0`，未考慮 `qty` 為 0 導致分母為 0 的情況。
    ```python
    return_rate = (unrealized_pl / (cost * qty)) if cost > 0 else 0
    ```

*   **根本原因 (Root Cause)**:
    *   在計算 `return_rate` 時，分母是 `cost * qty` (總成本)。
    *   原本的邏輯只防禦了 `cost == 0` (例如空投代幣)，但忽略了如果 `qty == 0` (例如已清倉但仍殘留在表上的資產)，分母 `cost * qty` 依然會變成 0，導致 `ZeroDivisionError`。

*   **解決方案 (Solution)**:
    *   改為檢查總成本是否大於 0。
    *   修正後：
        ```python
        total_cost = cost * qty
        return_rate = (unrealized_pl / total_cost) if total_cost > 0 else 0
        ```
    *   *學習點*：在進行除法運算時，必須確保分母的完整表達式不為零，而不僅僅是分母中的某個變數。

---
*持續更新中...*
