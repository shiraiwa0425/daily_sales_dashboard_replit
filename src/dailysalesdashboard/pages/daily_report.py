import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

def show_daily_report_page():
    """日別売上表ページを表示"""
    st.header("日別売上表")
    
    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年", range(2020, 2026), index=5, key="daily_year"
        )
    with col2:
        selected_month = st.selectbox(
            "月", range(1, 13), index=datetime.now().month - 1, key="daily_month"
        )
    
    # 選択された月の日数を取得
    _, last_day = calendar.monthrange(selected_year, selected_month)
    
    # 月間データのフィルタリング
    month_start = f"{selected_year}-{selected_month:02d}-01"
    month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"
    
    # データのフィルタリング
    month_data = st.session_state.data[
        (st.session_state.data['日付'] >= month_start) & 
        (st.session_state.data['日付'] <= month_end)
    ].copy()
    
    if month_data.empty:
        st.info(f"{selected_year}年{selected_month}月のデータはありません。「売上入力」から登録してください。")
        return
    
    # 日付ごとの集計
    daily_sales = month_data.groupby('日付')['売上金額'].sum().reset_index()
    daily_sales['日'] = daily_sales['日付'].str.split('-').str[2].astype(int)
    daily_sales = daily_sales.sort_values('日')
    
    # 時間帯別の集計
    time_sales = month_data.groupby(['日付', '時間帯'])['売上金額'].sum().reset_index()
    time_sales['日'] = time_sales['日付'].str.split('-').str[2].astype(int)
    
    # 支払方法別の集計
    payment_sales = month_data.groupby(['日付', '支払方法'])['売上金額'].sum().reset_index()
    payment_sales['日'] = payment_sales['日付'].str.split('-').str[2].astype(int)
    
    # 日別売上グラフ
    st.subheader("日別売上推移")
    fig = px.bar(
        daily_sales, 
        x='日', 
        y='売上金額',
        text_auto='.2s',
        title=f"{selected_year}年{selected_month}月 日別売上"
    )
    fig.update_layout(
        xaxis_title="日",
        yaxis_title="売上金額（円）",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 時間帯別グラフ
    st.subheader("時間帯別売上")
    
    # 時間帯別データの準備
    lunch_data = time_sales[time_sales['時間帯'] == '昼営業'].sort_values('日')
    dinner_data = time_sales[time_sales['時間帯'] == '夜営業'].sort_values('日')
    
    # 棒グラフ（昼夜比較）
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=lunch_data['日'],
        y=lunch_data['売上金額'],
        name='昼営業',
        marker_color='#1E88E5'
    ))
    
    fig.add_trace(go.Bar(
        x=dinner_data['日'],
        y=dinner_data['売上金額'],
        name='夜営業',
        marker_color='#FFC107'
    ))
    
    fig.update_layout(
        title=f"{selected_year}年{selected_month}月 時間帯別売上",
        xaxis_title="日",
        yaxis_title="売上金額（円）",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 詳細データ表示
    st.subheader("日別売上詳細")
    
    # データをピボットテーブルで整形
    pivot_time = time_sales.pivot_table(
        index='日', 
        columns='時間帯', 
        values='売上金額', 
        aggfunc='sum'
    ).reset_index()
    
    # 欠けている列があれば追加
    if '昼営業' not in pivot_time.columns:
        pivot_time['昼営業'] = 0
    if '夜営業' not in pivot_time.columns:
        pivot_time['夜営業'] = 0
    
    # 合計列を追加
    pivot_time['合計'] = pivot_time['昼営業'] + pivot_time['夜営業']
    pivot_time = pivot_time.sort_values('日')
    
    # 表示するデータを整形
    display_data = pivot_time[['日', '昼営業', '夜営業', '合計']].copy()
    
    # 表示
    st.dataframe(
        display_data.style.format({
            '昼営業': '{:,.0f}円',
            '夜営業': '{:,.0f}円',
            '合計': '{:,.0f}円'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # 月間集計
    st.subheader("月間集計")
    
    monthly_total = pivot_time['合計'].sum()
    lunch_total = pivot_time['昼営業'].sum()
    dinner_total = pivot_time['夜営業'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("昼営業合計", f"¥{lunch_total:,.0f}")
    col2.metric("夜営業合計", f"¥{dinner_total:,.0f}")
    col3.metric("月間合計", f"¥{monthly_total:,.0f}")