import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from ..utils import on_value_change, validate_input
from ..data.loader import save_data

def save_sales_data(selected_year, selected_month, sales_data, last_day):
    """売上データを保存する関数"""
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

def show_data_entry_page():
    """売上入力ページを表示"""
    st.header("月次売上データ入力")

    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年", range(2020, 2026), index=5
        )
    with col2:
        selected_month = st.selectbox(
            "月", range(1, 13), index=datetime.now().month - 1
        )

    # 年月が変更されたかチェック
    current_year_month = f"{selected_year}-{selected_month}"
    if st.session_state.previous_year_month != current_year_month:
        # セッション状態の完全なリセット
        st.session_state.sales_data = {}
        st.session_state.form_submitted = False
        st.session_state.previous_value = {}

        # 入力フィールドの状態を完全にリセット
        keys_to_delete = []
        for key in st.session_state.keys():
            if any(prefix in key for prefix in ['lunch_', 'dinner_', 'card_', 'paypay_', 'stella_', 'error_']):
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del st.session_state[key]

        st.session_state.previous_year_month = current_year_month

    # 選択された月の日数を取得
    _, last_day = calendar.monthrange(selected_year, selected_month)

    # 既存データの取得（月初から月末までの範囲で）
    month_start = f"{selected_year}-{selected_month:02d}-01"
    month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"
    existing_month_data = st.session_state.data[
        (st.session_state.data['日付'] >= month_start) &
        (st.session_state.data['日付'] <= month_end)
    ].copy()

    # 表形式での入力フォーム
    col_labels = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
    col_labels[0].write("日付")
    col_labels[1].write("昼営業売上")
    col_labels[2].write("夜営業売上")
    col_labels[3].write("カード売上")
    col_labels[4].write("PayPay売上")
    col_labels[5].write("stella売上")
    col_labels[6].write("合計")

    # 売上データの入力
    has_error = False
    total_lunch = 0
    total_dinner = 0
    total_card = 0
    total_paypay = 0
    total_stella = 0

    # 日ごとの入力フィールド
    for day in range(1, last_day + 1):
        # 入力フィールド表示・処理
        # (この部分は長くなるため一部省略)
        date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
        
        # 既存データの取得
        existing_data = existing_month_data[existing_month_data['日付'] == date_str]
        
        # 初期値の設定（すべて空に）
        values = {
            'lunch': 0, 'dinner': 0, 'card': 0, 'paypay': 0, 'stella': 0
        }
        
        # 既存データがある場合のみ値を設定
        if not existing_data.empty:
            # 時間帯での売上集計
            lunch_data = existing_data[existing_data['時間帯'] == '昼営業']
            dinner_data = existing_data[existing_data['時間帯'] == '夜営業']

            if not lunch_data.empty:
                values['lunch'] = lunch_data['売上金額'].sum()
            if not dinner_data.empty:
                values['dinner'] = dinner_data['売上金額'].sum()

            # 支払方法での売上集計
            if '支払方法' in existing_data.columns:
                for payment_type in ['card', 'paypay', 'stella']:
                    payment_data = existing_data[existing_data['支払方法'] == payment_type]
                    if not payment_data.empty:
                        values[payment_type] = payment_data['売上金額'].sum()

        cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
        cols[0].write(f"{day}日")
        
        # 各項目の入力フィールド
        sales_values = {}
        for i, (key, label) in enumerate([
            ('lunch', '昼営業'), ('dinner', '夜営業'), 
            ('card', 'カード'), ('paypay', 'PayPay'), ('stella', 'stella')
        ]):
            input_key = f"{key}_{day}"
            
            # エラー状態の初期化
            if f'error_{input_key}' not in st.session_state:
                st.session_state[f'error_{input_key}'] = ""
            
            # 入力フィールドを初期化
            if input_key not in st.session_state:
                # 既存データがある場合はその値を設定、ない場合は空文字列
                if values[key] > 0:
                    st.session_state[input_key] = str(int(values[key]))
                else:
                    st.session_state[input_key] = ""
            
            # 入力フィールドの表示
            sales_str = cols[i + 1].text_input(
                f"{label} {day}日",
                key=input_key,
                value=st.session_state[input_key],
                label_visibility="collapsed",
                help="",
                autocomplete="off",
                on_change=on_value_change,
                args=(input_key,)
            )
            
            # 検証済みの値を使用
            sales_values[key] = validate_input(sales_str, input_key)
            
            # エラー表示
            if st.session_state[f'error_{input_key}']:
                cols[i + 1].error(st.session_state[f'error_{input_key}'])
                has_error = True
        
        # 合計の計算と表示
        daily_total = sales_values['lunch'] + sales_values['dinner']
        cols[6].write(f"¥{daily_total:,.0f}")
        
        # 合計に加算
        total_lunch += sales_values['lunch']
        total_dinner += sales_values['dinner']
        total_card += sales_values['card']
        total_paypay += sales_values['paypay']
        total_stella += sales_values['stella']
        
        # セッション状態に保存
        st.session_state.sales_data[day] = sales_values

    # 月間合計の表示
    st.divider()
    total_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
    total_cols[0].write("**月間合計**")
    total_cols[1].write(f"**¥{total_lunch:,.0f}**")
    total_cols[2].write(f"**¥{total_dinner:,.0f}**")
    total_cols[3].write(f"**¥{total_card:,.0f}**")
    total_cols[4].write(f"**¥{total_paypay:,.0f}**")
    total_cols[5].write(f"**¥{total_stella:,.0f}**")
    total_cols[6].write(f"**¥{total_lunch + total_dinner:,.0f}**")

    # 保存ボタン
    with st.form("sales_form"):
        submitted = st.form_submit_button("保存", use_container_width=True)
        if submitted:
            if has_error:
                st.error("入力エラーがあります。修正してください。")
            else:
                save_success = save_sales_data(selected_year, selected_month, st.session_state.sales_data, last_day)
                if save_success:
                    st.success("売上データを保存しました！")
                    st.session_state.form_submitted = False
                    # 日別売上表に画面遷移
                    st.rerun()
                else:
                    st.error("データの保存中にエラーが発生しました。")
                    st.session_state.form_submitted = False