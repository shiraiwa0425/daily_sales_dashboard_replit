import streamlit as st
import pandas as pd
import os
from .processor import standardize_data, validate_sales_data

def load_data():
    """データを読み込み、標準化する関数"""
    try:
        if os.path.exists("sales_data.csv"):
            df = pd.read_csv("sales_data.csv")
            # データの標準化を適用
            return standardize_data(df)
        else:
            return pd.DataFrame(columns=["日付", "時間帯", "支払方法", "売上金額", "備考"])
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame(columns=["日付", "時間帯", "支払方法", "売上金額", "備考"])

def save_data(df):
    """データを保存する関数"""
    try:
        # データを検証
        if validate_sales_data(df):
            df.to_csv("sales_data.csv", index=False)
            return True
        else:
            st.error("データ形式が不正です")
            return False
    except Exception as e:
        st.error(f"データ保存エラー: {e}")
        return False