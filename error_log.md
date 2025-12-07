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

### 5. `uv add` 存取被拒與依賴損壞 (Access Denied & Broken Dependency)

*   **錯誤訊息 (Error Message)**:
    ```text
    error: failed to remove directory ...\protobuf-5.29.5.dist-info: 存取被拒。 (os error 5)
    warning: Failed to uninstall package ... due to missing `RECORD` file.
    ```
    發生在嘗試升級或重裝依賴 (`protobuf`) 時。

*   **根本原因 (Root Cause)**:
    *   **檔案鎖定**：首先是因為有 Python process (可能是測試腳本或 IDE 插件) 正在使用 `protobuf` 相關檔案，導致 `uv` 無法刪除舊版目錄，觸發 "存取被拒"。
    *   **狀態不一致**：由於刪除操作只成功了一半（部分檔案被刪除，部分被鎖定），導致套件的 metadata (`RECORD` file) 遺失。
    *   **自動修復**：第二次執行 `uv add` 時，`uv` 檢測到這個損壞狀態，雖然發出警告 (missing RECORD file)，但它夠聰明，直接強制覆蓋安裝了新版 (`protobuf==5.29.5`)，最終顯示安裝成功。

*   **解決方案 (Solution)**:
    *   雖然 `uv` 自動修復了，但為了保險起見，建議執行 `uv sync` 來確保環境一致性。
    *   如果還是報錯，手動刪除 `.venv` 資料夾並重新 `uv sync` 是最徹底的解法。
    *   *學習點*：在 Windows 上看到 "存取被拒" 後如果再次執行成功但有警告，通常代表套件管理工具進行了 Dirty Fix，需留意環境是否穩定。

### 6. Python 初始化編碼錯誤 (UnicodeDecodeError in site.py)

*   **錯誤訊息 (Error Message)**:
    ```text
    UnicodeDecodeError: 'cp950' codec can't decode byte 0xe6 in position 24: illegal multibyte sequence
    ```
    發生在執行 `uv run` 或啟動 Python 時，於 `site.py` 的 `addpackage` 階段崩潰。

*   **根本原因 (Root Cause)**:
    *   `uv` 在建立虛擬環境 `.venv` 時，產生了 `.pth` 檔案（如 `_investment_daily.pth`）指向專案路徑。
    *   專案路徑中包含中文字元（例如 `OneDrive\文件`）。`uv` 預設以 **UTF-8** 編碼寫入該路徑到 `.pth` 檔。
    *   在 Windows 上，Python 啟動時讀取 `.pth` 檔預設使用系統 ANSI 編碼（繁體中文系統為 **CP950/Big5**）。
    *   當 Python 嘗試用 CP950 解碼 UTF-8 編碼的中文字元（`0xE6...`）時，發生解碼錯誤。

*   **解決方案 (Solution)**:
    *   設定環境變數 `PYTHONUTF8=1`，強制 Python 使用 UTF-8 作為文件系統和 IO 的預設編碼。
    *   PowerShell 指令：`$env:PYTHONUTF8 = "1"`
    *   *學習點*：Windows 開發環境下，若路徑包含非 ASCII 字元，極易與 Python 預設編碼發生衝突。現代 Python 開發建議在 Windows 上常駐開啟 `PYTHONUTF8` 模式。

### 7. Gemini Model 404 (Model Not Found/Deprecated)

*   **錯誤訊息 (Error Message)**:
    ```text
    API 呼叫失敗: 404 models/gemini is not found for API version v1beta...
    ```
    發生在嘗試呼叫 `gemini-1.5-flash` 模型時。

*   **根本原因 (Root Cause)**:
    *   `gemini-1.5-flash` 可能已被棄用、API 版本變更，或需要使用更新的別名。
    *   Google AI Studio 的模型版本更新頻繁，舊版模型名稱可能失效。

*   **解決方案 (Solution)**:
    *   改用指向最新穩定版的通用別名：`gemini-flash-latest`。
    *   修改代碼：
        ```python
        model = genai.GenerativeModel('gemini-flash-latest')
        ```
    *   *學習點*：在使用雲端 AI API 時，若不想頻繁追蹤版本號，可優先使用官方提供的 Latest Alias (如 `gemini-flash-latest`, `gpt-4o`)，以確保長期可用性。

---
*持續更新中...*
