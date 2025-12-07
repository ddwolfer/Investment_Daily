# -*- coding: utf-8 -*-
"""
Google Sheet 服務 (Google Sheet Service)
負責連接 Google Sheets API 並讀取持倉數據。
"""

import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ..config import Config

class GoogleSheetService:
    def __init__(self):
        """初始化 Google Sheet 服務"""
        self.creds_file = Config.GOOGLE_CREDENTIALS_FILE
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.service = None
        
        # 如果憑證檔案存在才初始化，方便測試時不報錯
        if os.path.exists(self.creds_file):
            try:
                self.service = self._authenticate()
            except Exception as e:
                print(f"憑證驗證失敗: {e}")
        else:
            print(f"憑證檔不存在: {self.creds_file}，Google Sheet 服務將使用 Mock 數據模式。")

    def _authenticate(self):
        """驗證並建立 Sheet 服務實例"""
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file, scopes=self.scopes)
        return build('sheets', 'v4', credentials=creds)

    def get_portfolio_data(self, range_name="Sheet1!A:Z"):
        """
        讀取持倉數據並標準化
        返回: DataFrame 包含 [Symbol, Qty, Cost, MarketPrice, UnrealizedPL, ReturnRate, Type]
        """
        if not self.service:
            # Mock data for testing without credentials
            return self._get_mock_data()

        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.sheet_id,
                                        range=range_name).execute()
            values = result.get('values', [])

            if not values:
                print("Google Sheet 中沒有數據。")
                return pd.DataFrame()

            # 假設第一行是標題，轉為 DataFrame
            # 注意：如果 sheet 第一行不是 header，這裡需要調整
            df = pd.DataFrame(values[1:], columns=values[0])
            
            # 基本清洗：移除沒有 Symbol 的行
            if 'Symbol' in df.columns:
                df = df.dropna(subset=['Symbol'])
                df = df[df['Symbol'] != '']
            
            # 欄位對映與標準化
            column_mapping = {
                'Market Price': 'MarketPrice',
                'Unrealized P/L': 'UnrealizedPL',
                'Avg Cost': 'Cost',
                'Average Cost': 'Cost',
                'Price': 'MarketPrice',
                'P/L': 'UnrealizedPL'
            }
            df = df.rename(columns=column_mapping)
            
            # 確保必要欄位存在
            required_cols = ['Symbol', 'Qty', 'Cost', 'MarketPrice', 'UnrealizedPL']
            for col in required_cols:
                if col not in df.columns:
                    print(f"警告: Google Sheet 缺少欄位 {col}，將自動補零。")
                    df[col] = 0

            # 數值轉換 (移除 $ , 等符號並轉 float)
            for col in ['Qty', 'Cost', 'MarketPrice', 'UnrealizedPL']:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(r'[$,]', '', regex=True), 
                    errors='coerce'
                ).fillna(0)

            # 計算回報率 (ReturnRate) 如果沒有的話
            if 'ReturnRate' not in df.columns:
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
                # 可以加入更多判斷邏輯
                return 'Stock'

            df['Type'] = df['Symbol'].apply(determine_type)
            
            return df

        except Exception as e:
            print(f"讀取 Google Sheet 時發生錯誤: {e}")
            return self._get_mock_data() # 出錯時降級為 Mock 數據，方便除錯

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
