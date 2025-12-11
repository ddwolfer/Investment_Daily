# debug_env.py
import sys
import os

# 確保路徑
sys.path.append(os.getcwd())

from investment_bot.config import Config

print("--- ENV DEBUG ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"GOOGLE_SHEET_ID from Config: {Config.GOOGLE_SHEET_ID}")
print(f"Credentials File: {Config.GOOGLE_CREDENTIALS_FILE}")
print("-----------------")