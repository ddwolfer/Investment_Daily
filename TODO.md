# 專案待辦事項 (TODO List)

> 📅 最後更新：2025-12-12  
> 🎯 當前階段：功能驗證與測試

---

## 🔴 高優先級（Critical）

### 1. 測試 Market Data API 連接
- [ ] **驗證 yfinance (美股數據)**
  - 測試標的：TSLA, NVDA, IVV
  - 驗證項目：數據完整性、日期範圍、欄位正確性
  - 📁 測試腳本：`test_script/test_market_apis.py`（待建立）

- [ ] **驗證 ccxt/Binance (加密貨幣數據)**
  - 測試標的：BTC, ETH, SOL
  - 驗證項目：API 連接、交易對對映、數據格式
  
- [ ] **驗證 Fear & Greed Index API**
  - API 端點：https://api.alternative.me/fng/
  - 驗證項目：回傳值、錯誤處理、快取邏輯

### 2. 測試 LLM 服務 (Gemini)
- [ ] **驗證 Gemini API 連接**
  - 測試腳本已存在：`test_script/test_gemini.py`
  - 驗證模型：`gemini-flash-latest`
  
- [ ] **測試報告生成品質**
  - 輸入：測試用的持倉數據 + 技術信號
  - 驗證項目：Markdown 格式、繁體中文、風控官語氣
  
- [ ] **檢查 Token 用量與成本**
  - 記錄每次生成的 token 數量
  - 估算每日成本

### 3. 測試 Telegram Bot
- [ ] **驗證訊息發送功能**
  - 測試腳本：`test_script/test_telegram.py`（待建立）
  - 發送測試訊息到指定 Chat ID
  
- [ ] **測試 Markdown 渲染**
  - 驗證：粗體、斜體、表格、Emoji
  - 測試特殊字符轉義（`_`, `*`, `[`, `]` 等）

### 4. 端到端整合測試
- [ ] **執行完整 main.py 流程**
  - 從 Google Sheet 讀取 → API 抓取 → 技術分析 → LLM 生成 → Telegram 發送
  - 記錄執行時間與各階段耗時
  
- [ ] **驗證所有模組協作正常**
  - 快取機制運作
  - 資料庫儲存正確
  - 錯誤處理機制有效

---

## 🟡 中優先級（Important）

### 5. 錯誤處理優化
- [ ] **加強 API 失敗的 fallback 機制**
  - yfinance 失敗時的備援方案
  - ccxt Rate Limit 處理（Binance 限制：1200 requests/min）
  - Gemini API quota 超額處理
  
- [ ] **改善日誌輸出格式**
  - 加入時間戳記
  - 統一日誌格式（INFO/WARNING/ERROR）
  - 可選：使用 logging 模組替代 print

- [ ] **加入重試邏輯**
  - API 調用失敗時自動重試 3 次
  - 使用 exponential backoff

### 6. 性能與資料品質驗證
- [ ] **驗證快取 TTL 設定合理性**
  - 市場數據：60 分鐘是否合適？
  - 持倉數據：是否需要更短的快取時間？
  
- [ ] **檢查技術指標計算準確性**
  - 與交易平台（如 TradingView）對比驗證
  - 確保 EMA, RSI, MACD 數值正確

- [ ] **資料庫效能測試**
  - 模擬 1 年份的快照數據
  - 驗證查詢速度

---

## 🟢 低優先級（Nice to Have）

### 7. 定時排程
- [ ] **Windows Task Scheduler 設定**
  - 建立 .bat 執行腳本
  - 設定每日早上 8:00 執行
  - 加入錯誤通知機制
  
- [ ] **Linux/macOS cron job 設定**
  - 提供 crontab 範例
  - 處理虛擬環境路徑

### 8. 文檔完善
- [ ] **補充 Google Cloud 設定教學**
  - Service Account 建立步驟
  - API 啟用清單
  - 權限設定說明
  
- [ ] **建立 FAQ**
  - 常見錯誤與解決方案
  - API Rate Limit 處理
  - 成本估算

- [ ] **加入部署指南**
  - 雲端部署方案（AWS Lambda, GCP Cloud Run）
  - Docker 容器化

### 9. 功能擴充（未來）
- [ ] **歷史數據分析工具**
  - 查詢過去的持倉快照
  - 繪製淨值曲線圖
  - 回報率統計報表
  
- [ ] **更多技術指標**
  - ATR (Average True Range)
  - Fibonacci Retracement
  - Volume Profile

- [ ] **多通知管道**
  - Email 報告
  - Discord Webhook
  - LINE Notify

---

## ✅ 已完成功能

### 數據層
- [x] 雙 Google Sheet 支援（美股 + 加密貨幣）
  - 支援中文欄位對映
  - 支援不同欄位名稱（stock vs token）
  - 自動合併數據
  
- [x] 本地儲存架構（SQLite + Parquet）
  - Parquet 儲存市場數據（高效壓縮）
  - SQLite 儲存技術信號、持倉快照、市場情緒
  - 統一的 DataStore 介面

- [x] 快取機制
  - 市場數據：60 分鐘 TTL
  - 持倉數據：60 分鐘 TTL
  - 技術信號：每日計算一次
  - 快取命中時提升 20-30 倍速度

### 服務層
- [x] Market Data Service
  - yfinance 整合（美股）
  - ccxt/Binance 整合（加密貨幣）
  - Fear & Greed Index API
  
- [x] Technical Analysis Service
  - RSI（相對強弱指標）
  - MACD（指數平滑異同移動平均線）
  - EMA（指數移動平均線）
  - Bollinger Bands（布林通道）
  - 信號儲存到資料庫

- [x] Google Sheet Service
  - 雙來源讀取與合併
  - 欄位標準化與數值轉換
  - 百分比格式處理
  - 每日持倉快照

### 測試與工具
- [x] 本地儲存整合測試（`test_storage.py`）
- [x] Google Sheet 連線測試（`debug_google_sheet.py`）
- [x] Gemini API 測試（`test_gemini.py`）

---

## 🐛 已知問題

無（目前運作正常）

---

## 📝 開發備註

### API Rate Limits
- **Yahoo Finance**：無官方限制，但建議每秒不超過 2000 requests
- **Binance**：1200 requests/分鐘（已實作快取緩解）
- **Gemini API**：免費額度 15 RPM, 1M TPM, 1500 RPD

### 數據更新頻率
- 市場數據：每小時檢查一次（快取 60 分鐘）
- 技術信號：每日計算一次
- 持倉快照：每次執行 main.py 時儲存

### 環境配置重點
- Windows 環境需設定：`$env:PYTHONUTF8=1`（避免編碼錯誤）
- Google Sheets API 需啟用並分享給 Service Account
- Telegram Bot Token 需透過 @BotFather 申請

---

## 🎯 下一個里程碑

**目標**：完成端到端測試，確保 main.py 能完整執行並發送日報到 Telegram

**預計完成時間**：1-2 天

**驗收標準**：
1. ✅ 所有 API 測試通過
2. ✅ main.py 執行無錯誤
3. ✅ Telegram 成功收到完整報告
4. ✅ 快取與資料庫正常運作

