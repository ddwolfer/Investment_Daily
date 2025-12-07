# -*- coding: utf-8 -*-
"""
格式化工具 (Formatter Utilities)
負責數字格式化、顏色標記與 Emoji 處理。
"""

def format_currency(value):
    """將數值格式化為 USD 貨幣格式"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value):
    """將數值格式化為百分比"""
    try:
        val = float(value)
        return f"{val:.2f}%"
    except (ValueError, TypeError):
        return str(value)

def get_trend_emoji(value):
    """根據數值正負返回趨勢 Emoji"""
    try:
        val = float(value)
        if val > 0:
            return "🟢" 
        elif val < 0:
            return "🔴"
        else:
            return "⚪"
    except (ValueError, TypeError):
        return ""

