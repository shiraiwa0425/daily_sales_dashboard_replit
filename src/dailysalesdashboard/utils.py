import pandas as pd
from datetime import datetime
import os
import streamlit as st

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

def validate_input(value, key):
    """入力値の検証"""
    try:
        # 空文字列は0として扱う
        if value.strip() == "":
            st.session_state[f'error_{key}'] = ""
            return 0

        # 全角数字を半角数字に変換
        value = value.translate(str.maketrans('０１２３４５６７８９，．', '0123456789,.'))

        # 数値以外の文字が含まれているかチェック
        cleaned_value = value.replace(',', '')
        if not cleaned_value.replace('.', '').isdigit():
            st.session_state[f'error_{key}'] = "売上金額は数値で入力してください"
            return 0

        # カンマを除去して数値変換（小数点以下を切り捨て）
        num = int(float(cleaned_value))
        if num < 0:
            st.session_state[f'error_{key}'] = "売上金額は0以上の数値を入力してください"
            return 0

        # 正しい値が入力された場合、エラーメッセージをクリア
        st.session_state[f'error_{key}'] = ""
        return num
    except ValueError:
        st.session_state[f'error_{key}'] = "売上金額は数値で入力してください"
        return 0

def on_value_change(key):
    """入力値変更時のコールバック関数"""
    # 値を検証
    value = st.session_state[key]
    validated_value = validate_input(value, key)
    st.session_state[key] = str(validated_value)

    # キーから日付と種類を抽出
    payment_type, day = key.split('_')
    day = int(day)

    # セッション状態のsales_dataを更新
    if day not in st.session_state.sales_data:
        st.session_state.sales_data[day] = {}
    st.session_state.sales_data[day][payment_type] = validated_value

def generate_csv_download_link(df, filename="data.csv", link_text="CSVファイルをダウンロード"):
    """データフレームからCSVダウンロードリンクを生成"""
    import base64
    from io import StringIO
    
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href