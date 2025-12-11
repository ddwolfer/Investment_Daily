# -*- coding: utf-8 -*-
"""
Google Sheet 服務 (Google Sheet Service)
負責連接 Google Sheets API 並讀取持倉數據。
整合 DataStore 儲存持倉快照。
"""

import os
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ..config import Config
from ..utils.data_store import DataStore

class GoogleSheetService:
    def __init__(self):
        """初始化 Google Sheet 服務（支援雙來源：美股 + 加密貨幣）"""
        self.creds_file = Config.GOOGLE_CREDENTIALS_FILE
        self.stock_sheet_id = Config.GOOGLE_SHEET_ID_STOCK
        self.crypto_sheet_id = Config.GOOGLE_SHEET_ID_CRYPTO
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.service = None
        self.store = DataStore()
        
        # 驗證至少有一個 Sheet ID 被配置
        if not self.stock_sheet_id and not self.crypto_sheet_id:
            print(f"  [GoogleSheet] 警告：未配置任何 Sheet ID，將使用 Mock 數據模式。")
        
        # 如果憑證檔案存在才初始化，方便測試時不報錯
        if os.path.exists(self.creds_file):
            print(f"  [GoogleSheet] 憑證檔案存在: {self.creds_file}")
            try:
                self.service = self._authenticate()
                print("  [GoogleSheet] 驗證成功，服務已建立。")
                if self.stock_sheet_id:
                    print(f"  [GoogleSheet] Stock Sheet ID: {self.stock_sheet_id}")
                if self.crypto_sheet_id:
                    print(f"  [GoogleSheet] Crypto Sheet ID: {self.crypto_sheet_id}")
            except Exception as e:
                print(f"  [GoogleSheet] 憑證驗證失敗: {e}")
        else:
            print(f"  [GoogleSheet] 憑證檔不存在: {self.creds_file}，目前工作目錄: {os.getcwd()}")
            print(f"  [GoogleSheet] 將使用 Mock 數據模式。")

    def _authenticate(self):
        """驗證並建立 Sheet 服務實例"""
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file, scopes=self.scopes)
        return build('sheets', 'v4', credentials=creds)
    
    def _fetch_single_sheet(self, sheet_id, range_name, source_label="Sheet"):
        """
        讀取單一 Google Sheet 並標準化
        
        Args:
            sheet_id: Google Sheet ID
            range_name: 範圍名稱 (例如: "總損益!A:Z")
            source_label: 來源標籤，用於 debug 輸出 (例如: "美股", "加密貨幣")
        
        Returns:
            pandas.DataFrame: 標準化的持倉數據，失敗時返回空 DataFrame
        """
        if not sheet_id:
            return pd.DataFrame()
        
        if not self.service:
            print(f"  [GoogleSheet] 服務未初始化，無法讀取 {source_label}。")
            return pd.DataFrame()
        
        try:
            print(f"  [GoogleSheet] 正在讀取 {source_label} (ID: {sheet_id}, Range: {range_name})...")
            sheet = self.service.spreadsheets()
            
            # 先嘗試讀取，如果失敗可能是頁簽名稱不對
            try:
                result = sheet.values().get(spreadsheetId=sheet_id,
                                            range=range_name).execute()
                values = result.get('values', [])
            except Exception as range_error:
                # 如果 Range 錯誤，嘗試列出所有可用的頁簽
                print(f"  [GoogleSheet] {source_label} Range 錯誤: {range_error}")
                print(f"  [GoogleSheet] 嘗試列出 {source_label} 的所有可用頁簽...")
                try:
                    metadata = sheet.get(spreadsheetId=sheet_id).execute()
                    sheet_names = [s['properties']['title'] for s in metadata.get('sheets', [])]
                    print(f"  [GoogleSheet] {source_label} 可用的頁簽: {sheet_names}")
                    if sheet_names:
                        # 使用第一個頁簽
                        first_sheet = sheet_names[0]
                        print(f"  [GoogleSheet] {source_label} 改用第一個頁簽: {first_sheet}")
                        range_name = f"{first_sheet}!A:Z"
                        result = sheet.values().get(spreadsheetId=sheet_id,
                                                    range=range_name).execute()
                        values = result.get('values', [])
                    else:
                        print(f"  [GoogleSheet] {source_label} 中沒有找到任何頁簽")
                        return pd.DataFrame()
                except Exception as e2:
                    print(f"  [GoogleSheet] 無法讀取 {source_label}: {e2}")
                    return pd.DataFrame()

            if not values:
                print(f"  [GoogleSheet] {source_label} API 回傳成功，但沒有數據 (values is empty)。")
                return pd.DataFrame()
            
            print(f"  [GoogleSheet] 成功讀取 {source_label} {len(values)} 行數據。")
            df = pd.DataFrame(values[1:], columns=values[0])
            
            # 基本清洗：移除沒有 stock/token 的行
            if 'stock' in df.columns:
                df = df.dropna(subset=['stock'])
                df = df[df['stock'] != '']
            elif 'token' in df.columns:
                # 加密貨幣 Sheet 使用 'token' 欄位
                df = df.dropna(subset=['token'])
                df = df[df['token'] != '']
            elif 'Symbol' in df.columns:
                # 兼容舊的英文欄位名稱
                df = df.dropna(subset=['Symbol'])
                df = df[df['Symbol'] != '']
            else:
                print(f"  [GoogleSheet] {source_label} 警告: 找不到 'stock'、'token' 或 'Symbol' 欄位")
            
            # 欄位對映與標準化：將中文欄位對映到程式內部使用的標準名稱
            column_mapping = {
                # 美股 Sheet 欄位 -> 標準名稱
                'stock': 'Symbol',
                '總數量': 'Qty',
                '每股成本': 'Cost',
                '總投入USD': 'TotalCost',  # 保留作為參考，但主要用 Cost
                '目前價格': 'MarketPrice',
                '目前價值': 'MarketValue',  # 保留作為參考
                '損益': 'UnrealizedPL',
                '獲益率': 'ReturnRate',
                # 加密貨幣 Sheet 欄位 -> 標準名稱
                'token': 'Symbol',
                '每顆成本': 'Cost',
                '總投入USDT': 'TotalCost',
                # 兼容舊的英文欄位名稱
                'Market Price': 'MarketPrice',
                'Unrealized P/L': 'UnrealizedPL',
                'Avg Cost': 'Cost',
                'Average Cost': 'Cost',
                'Price': 'MarketPrice',
                'P/L': 'UnrealizedPL'
            }
            df = df.rename(columns=column_mapping)
            
            # 確保必要欄位存在（使用標準名稱）
            required_cols = ['Symbol', 'Qty', 'Cost', 'MarketPrice', 'UnrealizedPL']
            for col in required_cols:
                if col not in df.columns:
                    print(f"  [GoogleSheet] {source_label} 警告: 缺少欄位 {col}，將自動補零。")
                    df[col] = 0

            # 數值轉換 (移除 $ , 等符號並轉 float)
            numeric_cols = ['Qty', 'Cost', 'MarketPrice', 'UnrealizedPL', 'TotalCost', 'MarketValue']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.replace(r'[$,]', '', regex=True), 
                        errors='coerce'
                    ).fillna(0)

            # 處理百分比欄位 (ReturnRate)
            if 'ReturnRate' in df.columns:
                # 將 "34.8%" 轉換為 0.348
                df['ReturnRate'] = df['ReturnRate'].astype(str).str.replace('%', '').apply(
                    lambda x: pd.to_numeric(x, errors='coerce') / 100 if x.strip() != '' else 0
                ).fillna(0)
            else:
                # 如果沒有 ReturnRate 欄位，自動計算
                df['ReturnRate'] = df.apply(
                    lambda row: (row['MarketPrice'] - row['Cost']) / row['Cost'] 
                    if row['Cost'] != 0 else 0, 
                    axis=1
                )

            # 區分 Type (Crypto / Stock)
            crypto_keys = set(Config.CRYPTO_MAPPING.keys())
            
            def determine_type(symbol):
                symbol = str(symbol).upper().strip()
                if symbol in crypto_keys:
                    return 'Crypto'
                return 'Stock'

            df['Type'] = df['Symbol'].apply(determine_type)
            
            print(f"  [GoogleSheet] {source_label} 數據處理完成，共 {len(df)} 筆。")
            return df
            
        except Exception as e:
            print(f"  [GoogleSheet] 讀取 {source_label} 時發生錯誤: {e}")
            return pd.DataFrame()

    def get_portfolio_data(self, range_name=None):
        """
        讀取持倉數據並標準化（支援雙來源：美股 + 加密貨幣）
        Logic: Check Cache (1h TTL) -> Fetch from Multiple Sheets -> Merge -> Save Snapshot & Update Cache
        """
        # 如果沒有指定 range_name，使用 Config 中的預設值
        if range_name is None:
            range_name = Config.GOOGLE_SHEET_RANGE
        
        cache_key = "portfolio_data"
        
        # 1. Check Cache (TTL: 60 minutes)
        cached_data = self.store.get_cache(cache_key)
        if cached_data:
            # print("  [Portfolio Cache Hit]")
            # Cache stores JSON, need to convert back to DataFrame
            return pd.DataFrame(cached_data)

        # 2. Fetch from API (支援雙來源)
        stock_df = pd.DataFrame()
        crypto_df = pd.DataFrame()
        
        # 2.1 讀取美股 Sheet
        if self.stock_sheet_id:
            stock_df = self._fetch_single_sheet(self.stock_sheet_id, range_name, "美股")
        
        # 2.2 讀取加密貨幣 Sheet
        if self.crypto_sheet_id:
            crypto_df = self._fetch_single_sheet(self.crypto_sheet_id, range_name, "加密貨幣")
        
        # 2.3 合併數據
        if not stock_df.empty and not crypto_df.empty:
            # 兩個都有數據，需要合併
            # 先確保欄位一致，補齊缺失的欄位
            all_cols = list(set(stock_df.columns) | set(crypto_df.columns))
            for col in all_cols:
                if col not in stock_df.columns:
                    stock_df[col] = 0 if col in ['Qty', 'Cost', 'MarketPrice', 'UnrealizedPL', 'ReturnRate', 'TotalCost', 'MarketValue'] else ''
                if col not in crypto_df.columns:
                    crypto_df[col] = 0 if col in ['Qty', 'Cost', 'MarketPrice', 'UnrealizedPL', 'ReturnRate', 'TotalCost', 'MarketValue'] else ''
            
            # 轉成 dict list 再重新建立 DataFrame 避免 index 衝突
            combined_data = stock_df.to_dict('records') + crypto_df.to_dict('records')
            df = pd.DataFrame(combined_data)
            print(f"  [GoogleSheet] 合併完成，共 {len(df)} 筆持倉數據 (美股: {len(stock_df)}, 加密貨幣: {len(crypto_df)})。")
        elif not stock_df.empty:
            # 只有美股數據
            df = stock_df.copy()
            print(f"  [GoogleSheet] 只讀取到美股數據，共 {len(df)} 筆。")
        elif not crypto_df.empty:
            # 只有加密貨幣數據
            df = crypto_df.copy()
            print(f"  [GoogleSheet] 只讀取到加密貨幣數據，共 {len(df)} 筆。")
        else:
            # 如果兩個都沒有數據，使用 Mock Data（僅限測試）
            print("  [GoogleSheet] 未讀取到任何數據，使用 Mock Data。")
            df = self._get_mock_data()

        # 3. Save Snapshot to DB & Cache
        if not df.empty:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Save historical snapshot to SQLite
            self.store.save_portfolio_snapshot(df, today)
            
            # Save to Cache (for short-term reuse)
            # Convert DataFrame to dict record for JSON serialization
            self.store.set_cache(cache_key, df.to_dict('records'), ttl_minutes=60)
            
        return df

    def _get_mock_data(self):
        """測試用的假數據"""
        print("⚠️ 使用 Mock Data...")
        data = {
            'Symbol': ['TSLA', 'NVDA', 'BTC', 'ETH', 'SOL'],
            'Qty': [10, 50, 0.5, 2.0, 100],
            'Cost': [200, 400, 30000, 2000, 20],
            'MarketPrice': [250, 800, 65000, 3500, 150],
            'UnrealizedPL': [500, 20000, 17500, 3000, 13000],
            'Type': ['Stock', 'Stock', 'Crypto', 'Crypto', 'Crypto']
        }
        df = pd.DataFrame(data)
        # 計算 ReturnRate
        df['ReturnRate'] = (df['MarketPrice'] - df['Cost']) / df['Cost']
        return df
