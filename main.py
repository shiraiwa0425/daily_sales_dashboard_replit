import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import json
from utils import load_data, save_data, validate_sales_data
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

# ページ設定
st.set_page_config(
    page_title="飲食店売上管理システム",
    page_icon="icon.svg",
    layout="wide"
)

# CSSの読み込み
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# SVGの読み込みとbase64エンコード
with open('icon.svg', 'r') as f:
    svg_content = f.read()
    b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    svg_url = f'data:image/svg+xml;base64,{b64}'

# タイトル（SVGを使用）
st.markdown(
    f"""
    <div class="title-container">
        <img src="{svg_url}" class="title-icon" alt="アジフライアイコン">
        <h1>飲食店売上管理システム</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# セッション状態の初期化
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'previous_year_month' not in st.session_state:
    st.session_state.previous_year_month = None
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'previous_value' not in st.session_state:
    st.session_state.previous_value = {}

# サイドバー
st.sidebar.header("メニュー")
current_page = st.sidebar.radio(
    label="",  # ラベルを空文字列に設定
    options=["売上入力", "日別売上表", "月別売上表", "売上分析", "データ管理"]
)

if current_page == "売上入力":
    st.header("月次売上データ入力")

    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年",
            range(2020, 2026),
            index=5  # 2025年をデフォルト選択
        )
    with col2:
        selected_month = st.selectbox(
            "月",
            range(1, 13),
            index=datetime.now().month - 1
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

    for day in range(1, last_day + 1):
        date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"

        # 既存データの取得
        existing_data = existing_month_data[
            existing_month_data['日付'] == date_str
        ]

        # 初期値の設定（すべて空に）
        values = {
            'lunch': 0,
            'dinner': 0,
            'card': 0,
            'paypay': 0,
            'stella': 0
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
            ('lunch', '昼営業'),
            ('dinner', '夜営業'),
            ('card', 'カード'),
            ('paypay', 'PayPay'),
            ('stella', 'stella')
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
                value=st.session_state[input_key],  # セッション状態から値を取得
                label_visibility="collapsed",
                help="",
                autocomplete="off",
                on_change=lambda: on_value_change(input_key)
            )

            # 検証済みの値を使用
            sales_values[key] = validate_input(sales_str, input_key)

            # エラー表示
            if st.session_state[f'error_{input_key}']:
                cols[i + 1].error(st.session_state[f'error_{input_key}'])
                has_error = True

        # 合計の計算と表示（昼営業と夜営業のみ）
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
    total_cols[6].write(f"**¥{total_lunch + total_dinner:,.0f}**")  # 昼営業と夜営業のみの合計

    # 保存ボタン（フォーム内）
    with st.form("sales_form"):
        submitted = st.form_submit_button("保存", use_container_width=True)

        if submitted and not st.session_state.form_submitted:
            st.session_state.form_submitted = True

            if has_error:
                st.error("入力エラーがあります。修正してください。")
                st.session_state.form_submitted = False
            else:
                save_success = save_sales_data(selected_year, selected_month, st.session_state.sales_data, last_day)
                if save_success:
                    st.success("売上データを保存しました！")
                    # 日別売上表に画面遷移
                    current_page = "日別売上表"
                    st.session_state.form_submitted = False
                else:
                    st.error("データの保存中にエラーが発生しました。")
                    st.session_state.form_submitted = False

elif current_page == "月別売上表":
    st.header("月別売上表")

    # 年の選択
    selected_year = st.selectbox(
        "年の選択",
        range(2020, 2026),
        index=5  # 2025年をデフォルト選択
    )

    if not st.session_state.data.empty:
        # 年間データの取得と月別集計
        year_start = f"{selected_year}-01-01"
        year_end = f"{selected_year}-12-31"

        year_data = st.session_state.data[
            (st.session_state.data['日付'] >= year_start) &
            (st.session_state.data['日付'] <= year_end)
        ].copy()  # コピーを作成

        if not year_data.empty:
            # 月別データの集計
            year_data['月'] = pd.to_datetime(year_data['日付']).dt.month
            monthly_data = year_data.groupby(['月', '時間帯'])['売上金額'].sum().reset_index()

            # 時間帯別のデータフレームを作成
            lunch_data = monthly_data[monthly_data['時間帯'] == '昼営業'].set_index('月')['売上金額']
            dinner_data = monthly_data[monthly_data['時間帯'] == '夜営業'].set_index('月')['売上金額']

            # 月別サマリーの作成
            monthly_summary = pd.DataFrame({
                '昼営業': lunch_data,
                '夜営業': dinner_data
            }).fillna(0)

            # 総売上列を追加
            monthly_summary['総売上'] = monthly_summary['昼営業'] + monthly_summary['夜営業']

            # インデックスをリセットして月列を追加
            monthly_summary = monthly_summary.reset_index()

            # 月名を追加
            monthly_summary['月名'] = monthly_summary['月'].apply(lambda x: f"{x}月")

            # 表示用にフォーマット
            formatted_summary = monthly_summary.copy()
            for col in ['昼営業', '夜営業', '総売上']:
                formatted_summary[col] = formatted_summary[col].apply(lambda x: f"¥{x:,.0f}")

            # 合計行を追加
            total_row = pd.DataFrame([{
                '月': 13,
                '月名': '合計',
                '昼営業': f"¥{monthly_summary['昼営業'].sum():,.0f}",
                '夜営業': f"¥{monthly_summary['夜営業'].sum():,.0f}",
                '総売上': f"¥{monthly_summary['総売上'].sum():,.0f}"
            }])

            formatted_summary = pd.concat([formatted_summary, total_row])

            # サマリー指標の表示
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("年間昼営業総売上", f"¥{monthly_summary['昼営業'].sum():,.0f}")
            with col2:
                st.metric("年間夜営業総売上", f"¥{monthly_summary['夜営業'].sum():,.0f}")
            with col3:
                st.metric("年間総売上", f"¥{monthly_summary['総売上'].sum():,.0f}")

            # タブでグラフと表を切り替え
            tab1, tab2 = st.tabs(["表形式表示", "グラフ表示"])

            with tab1:
                # 表形式での表示
                st.dataframe(
                    formatted_summary[['月名', '昼営業', '夜営業', '総売上']],
                    use_container_width=True,
                    hide_index=True
                )

            with tab2:
                # 月別売上推移グラフ
                fig = go.Figure()

                # 昼営業のライン
                fig.add_trace(go.Scatter(
                    x=monthly_summary['月名'],
                    y=monthly_summary['昼営業'],
                    name='昼営業',
                    line=dict(color='#1f77b4', width=2)
                ))

                # 夜営業のライン
                fig.add_trace(go.Scatter(
                    x=monthly_summary['月名'],
                    y=monthly_summary['夜営業'],
                    name='夜営業',
                    line=dict(color='#ff7f0e', width=2)
                ))

                # 総売上の棒グラフ
                fig.add_trace(go.Bar(
                    x=monthly_summary['月名'],
                    y=monthly_summary['総売上'],
                    name='総売上',
                    opacity=0.3,
                    marker_color='#2ca02c'
                ))

                # グラフのレイアウト設定
                fig.update_layout(
                    title=f"{selected_year}年 月別売上推移",
                    xaxis_title="月",
                    yaxis_title="売上金額（円）",
                    hovermode='x unified',
                    barmode='relative'
                )

                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info(f"{selected_year}年のデータはありません。")

elif current_page == "売上分析":
    st.header("売上分析")

    # 期間選択
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日",
                                   datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("終了日", datetime.now())

    if not st.session_state.data.empty:
        # データのフィルタリング
        mask = (pd.to_datetime(st.session_state.data['日付']) >= pd.to_datetime(start_date)) & \
               (pd.to_datetime(st.session_state.data['日付']) <= pd.to_datetime(end_date))
        filtered_data = st.session_state.data[mask].copy()  # コピーを作成

        if not filtered_data.empty:
            # 集計データの表示
            lunch_total = filtered_data[filtered_data['時間帯'] == '昼営業']['売上金額'].sum()
            dinner_total = filtered_data[filtered_data['時間帯'] == '夜営業']['売上金額'].sum()
            total_sales = lunch_total + dinner_total

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("期間中昼営業総売上", f"¥{lunch_total:,.0f}")
            with col2:
                st.metric("期間中夜営業総売上", f"¥{dinner_total:,.0f}")
            with col3:
                st.metric("期間中総売上", f"¥{total_sales:,.0f}")

            # グラフ表示
            tab1, tab2 = st.tabs(["日次推移", "時間帯別"])

            with tab1:
                # 日次売上推移グラフ（時間帯別）
                daily_sales = filtered_data.groupby(['日付', '時間帯'])['売上金額'].sum().reset_index()
                fig = px.bar(daily_sales, x='日付', y='売上金額', color='時間帯',
                            title="日次売上推移（時間帯別）",
                            labels={'売上金額': '売上金額（円）'},
                            barmode='group')
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                # 時間帯別売上構成
                time_sales = filtered_data.groupby('時間帯')['売上金額'].sum()
                fig = px.pie(values=time_sales.values,
                            names=time_sales.index,
                            title="時間帯別売上構成")
                st.plotly_chart(fig, use_container_width=True)

elif current_page == "日別売上表":
    st.header("日別売上表")

    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年",
            range(2020, 2026),
            index=5  # 2025年をデフォルト選択
        )
    with col2:
        selected_month = st.selectbox(
            "月",
            range(1, 13),
            index=datetime.now().month - 1
        )

    # 選択された月の日数を取得
    _, last_day = calendar.monthrange(selected_year, selected_month)

    if not st.session_state.data.empty:
        # 月のデータを取得
        month_start = f"{selected_year}-{selected_month:02d}-01"
        month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"

        month_data = st.session_state.data[
            (st.session_state.data['日付'] >= month_start) &
            (st.session_state.data['日付'] <= month_end)
        ].copy()  # コピーを作成

        if not month_data.empty:
            # 集計データを表示
            lunch_total = month_data[month_data['時間帯'] == '昼営業']['売上金額'].sum()
            dinner_total = month_data[month_data['時間帯'] == '夜営業']['売上金額'].sum()
            total = lunch_total + dinner_total

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("月間昼営業売上", f"¥{lunch_total:,.0f}")
            with col2:
                st.metric("月間夜営業売上", f"¥{dinner_total:,.0f}")
            with col3:
                st.metric("月間総売上", f"¥{total:,.0f}")

            try:
                # 日付ごとのデータを準備
                daily_data = month_data.groupby(['日付', '時間帯'])['売上金額'].sum().reset_index()

                # 時間帯別のデータフレームを作成
                lunch_data = daily_data[daily_data['時間帯'] == '昼営業'].set_index('日付')['売上金額']
                dinner_data = daily_data[daily_data['時間帯'] == '夜営業'].set_index('日付')['売上金額']

                # 日別サマリーの作成
                daily_summary = pd.DataFrame({
                    '昼営業': lunch_data,
                    '夜営業': dinner_data
                }).fillna(0)

                # インデックスをリセットして日付列を追加
                daily_summary = daily_summary.reset_index()

                # 総売上列を追加
                daily_summary['総売上'] = daily_summary['昼営業'] + daily_summary['夜営業']

                # データを日付でソート（過去から未来）
                daily_summary = daily_summary.sort_values('日付', ascending=True)

                # 表示用にフォーマット
                formatted_summary = daily_summary.copy()
                for col in ['昼営業', '夜営業', '総売上']:
                    formatted_summary[col] = formatted_summary[col].apply(lambda x: f"¥{x:,.0f}")

                # 合計行を追加
                total_row = pd.DataFrame([{
                    '日付': '合計',
                    '昼営業': f"¥{daily_summary['昼営業'].sum():,.0f}",
                    '夜営業': f"¥{daily_summary['夜営業'].sum():,.0f}",
                    '総売上': f"¥{daily_summary['総売上'].sum():,.0f}"
                }])

                formatted_summary = pd.concat([formatted_summary, total_row])

                # 表の表示
                st.dataframe(
                    formatted_summary,
                    use_container_width=True,
                    hide_index=True
                )
            except Exception as e:
                st.error(f"データの集計中にエラーが発生しました: {str(e)}")
                st.info("選択期間内のデータを確認してください。")
        else:
            st.info(f"{selected_year}年{selected_month}月のデータはありません。")

elif current_page == "データ管理":
    st.header("データ管理")

    if not st.session_state.data.empty:
        # 期間選択
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日",
                                     datetime.now() - timedelta(days=30),
                                     key="data_start_date")
        with col2:
            end_date = st.date_input("終了日",
                                   datetime.now(),
                                   key="data_end_date")

        # データのフィルタリング
        mask = (pd.to_datetime(st.session_state.data['日付']) >= pd.to_datetime(start_date)) & \
               (pd.to_datetime(st.session_state.data['日付']) <= pd.to_datetime(end_date))
        filtered_data = st.session_state.data[mask].copy()

        if not filtered_data.empty:
            # データテーブル表示
            st.subheader("売上データ一覧")

            # データの表示用にコピーを作成
            display_data = filtered_data.copy()

            # 日付でソート
            display_data = display_data.sort_values('日付', ascending=False)

            # 日付ごとの各種売上を集計
            pivoted_data = pd.pivot_table(
                display_data,
                index=['日付'],
                columns=['時間帯'],
                values='売上金額',
                aggfunc='sum',
                fill_value=0
            ).reset_index()

            # 必要な列を作成
            result_data = pd.DataFrame()
            result_data['日付'] = pivoted_data['日付']
            result_data['昼営業'] = pivoted_data['昼営業'].astype(int)
            result_data['夜営業'] = pivoted_data['夜営業'].astype(int)
            result_data['カード'] = 0  # Placeholder for card sales (needs to be calculated from original data if available)
            result_data['PayPay'] = 0  # Placeholder for PayPay sales (needs to be calculated from original data if available)
            result_data['stella'] = 0  # Placeholder for stella sales (needs to be calculated from original data if available)

            # 表示用にデータをフォーマット
            formatted_data = result_data.style.format({
                "昼営業": "¥{:,.0f}",
                "夜営業": "¥{:,.0f}",
                "カード": "¥{:,.0f}",
                "PayPay": "¥{:,.0f}",
                "stella": "¥{:,.0f}"
            })

            # データテーブルの表示
            st.dataframe(
                formatted_data,
                use_container_width=True,
                hide_index=True
            )

            # CSVエクスポート（直接ダウンロード）
            st.divider()
            csv = result_data.to_csv(index=False)
            st.download_button(
                label="CSVエクスポート",
                data=csv,
                file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("選択された期間のデータがありません。")
    else:
        st.info("登録されているデータがありません。")