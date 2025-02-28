import pandas as pd
from datetime import datetime
import os

def load_data():
    """データの読み込み"""
    try:
        if os.path.exists('sales_data.csv'):
            return pd.read_csv('sales_data.csv')
        return pd.DataFrame(columns=['日付', '時間帯', '支払方法', '売上金額', '備考'])
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        return pd.DataFrame(columns=['日付', '時間帯', '支払方法', '売上金額', '備考'])

def save_data(df):
    """データの保存"""
    try:
        df.to_csv('sales_data.csv', index=False)
        return True
    except Exception as e:
        print(f"データ保存エラー: {e}")
        return False

def validate_sales_data(date, amount):
    """売上データのバリデーション"""
    try:
        # 日付が未来でないことを確認
        if date > datetime.now().date():
            return False

        # 金額が正の数であることを確認
        if amount < 0:
            return False

        return True
    except Exception as e:
        print(f"バリデーションエラー: {e}")
        return False