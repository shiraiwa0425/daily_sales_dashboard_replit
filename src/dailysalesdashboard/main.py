import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import json
from .utils import load_data, save_data, validate_sales_data

import base64

# 入力値の検証用関数
def validate_input(value, key):
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

def save_sales_data(selected_year, selected_month, sales_data, last_day):
    """売上データを保存する共通関数"""
    try:
        # 新しいデータの作成
        new_records = []
        for day, values in sales_data.items():
            date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"

            for payment_type, amount in values.items():
                if amount > 0:
                    new_records.append({
                        "日付": date_str,
                        "時間帯": "昼営業" if payment_type == "lunch" else "夜営業",
                        "支払方法": payment_type,
                        "売上金額": amount,
                        "備考": ""
                    })

        if new_records:
            # 選択された月のデータを削除
            month_start = f"{selected_year}-{selected_month:02d}-01"
            month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"

            # 既存のデータから選択月のデータを除外
            mask = ~((st.session_state.data['日付'] >= month_start) &
                     (st.session_state.data['日付'] <= month_end))
            st.session_state.data = st.session_state.data.loc[mask].copy()

            # 新しいデータを追加
            new_df = pd.DataFrame(new_records)
            st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)

            # データを保存
            return save_data(st.session_state.data)
    except Exception as e:
        print(f"データ保存エラー: {e}")
        return False

# 入力値変更時のコールバック関数
def on_value_change(key):
    """
    入力値の検証のみを行う関数
    """
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

def main():
    """メインアプリケーション関数"""
    st.title("Daily Sales Dashboard")
    
    # ダッシュボードのコンテンツをここに配置
    # データの読み込み、グラフの作成などの処理
    
    # データサンプル（実際のデータに置き換えてください）
    data = {
        'Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Sales': [100, 120, 90, 150, 130]
    }
    df = pd.DataFrame(data)
    
    # グラフの作成
    fig = px.line(df, x='Date', y='Sales', title='Daily Sales')
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()