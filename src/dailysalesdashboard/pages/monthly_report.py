import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

def show_monthly_report_page():
    """月別売上表ページを表示"""
    st.header("月別売上表")
    
    # 年選択
    selected_year = st.selectbox(
        "年", range(2020, 2026), index=5, key="monthly_year"
    )
    
    # 年間データのフィルタリング
    year_start = f"{selected_year}-01-01"
    year_end = f"{selected_year}-12-31"
    
    # データのフィルタリング
    year_data = st.session_state.data[
        (st.session_state.data['日付'] >= year_start) & 
        (st.session_state.data['日付'] <= year_end)
    ].copy()
    
    if year_data.empty:
        st.info(f"{selected_year}年のデータはありません。「売上入力」から登録してください。")
        return
    
    # 日付から月情報を抽出
    year_data['月'] = year_data['日付'].str.split('-').str[1].astype(int)
    
    # 月ごとの集計
    monthly_sales = year_data.groupby('月')['売上金額'].sum().reset_index()
    
    # 時間帯別の集計
    monthly_time_sales = year_data.groupby(['月', '時間帯'])['売上金額'].sum().reset_index()
    
    # 支払方法別の集計
    monthly_payment_sales = year_data.groupby(['月', '支払方法'])['売上金額'].sum().reset_index()
    
    # 月別売上グラフ
    st.subheader("月別売上推移")
    fig = px.bar(
        monthly_sales, 
        x='月', 
        y='売上金額',
        text_auto='.2s',
        title=f"{selected_year}年 月別売上"
    )
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13))
        ),
        xaxis_title="月",
        yaxis_title="売上金額（円）",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 時間帯別グラフ
    st.subheader("時間帯別売上")
    
    # 時間帯別データの準備
    lunch_data = monthly_time_sales[monthly_time_sales['時間帯'] == '昼営業']
    dinner_data = monthly_time_sales[monthly_time_sales['時間帯'] == '夜営業']
    
    # 棒グラフ（昼夜比較）
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=lunch_data['月'],
        y=lunch_data['売上金額'],
        name='昼営業',
        marker_color='#1E88E5'
    ))
    
    fig.add_trace(go.Bar(
        x=dinner_data['月'],
        y=dinner_data['売上金額'],
        name='夜営業',
        marker_color='#FFC107'
    ))
    
    fig.update_layout(
        title=f"{selected_year}年 時間帯別売上",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13))
        ),
        xaxis_title="月",
        yaxis_title="売上金額（円）",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 詳細データ表示
    st.subheader("月別売上詳細")
    
    # データをピボットテーブルで整形
    pivot_time = monthly_time_sales.pivot_table(
        index='月', 
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
    pivot_time = pivot_time.sort_values('月')
    
    # 表示するデータを整形
    month_names = {
        1: '1月', 2: '2月', 3: '3月', 4: '4月', 
        5: '5月', 6: '6月', 7: '7月', 8: '8月', 
        9: '9月', 10: '10月', 11: '11月', 12: '12月'
    }
    
    # 全ての月のデータを作成（データがない月もゼロで表示）
    all_months = pd.DataFrame({'月': range(1, 13)})
    display_data = all_months.merge(pivot_time, on='月', how='left').fillna(0)
    display_data['月名'] = display_data['月'].map(month_names)
    
    # 表示
    st.dataframe(
        display_data[['月名', '昼営業', '夜営業', '合計']].style.format({
            '昼営業': '{:,.0f}円',
            '夜営業': '{:,.0f}円',
            '合計': '{:,.0f}円'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # 年間集計
    st.subheader("年間集計")
    
    yearly_total = display_data['合計'].sum()
    yearly_lunch = display_data['昼営業'].sum()
    yearly_dinner = display_data['夜営業'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("昼営業合計", f"¥{yearly_lunch:,.0f}")
    col2.metric("夜営業合計", f"¥{yearly_dinner:,.0f}")
    col3.metric("年間合計", f"¥{yearly_total:,.0f}")