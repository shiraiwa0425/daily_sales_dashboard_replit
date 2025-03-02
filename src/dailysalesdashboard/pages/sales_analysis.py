import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

def show_sales_analysis_page():
    """売上分析ページを表示"""
    st.header("売上分析")
    
    # タブの設定
    tab1, tab2, tab3 = st.tabs(["日別推移", "曜日分析", "支払方法分析"])
    
    # データの取得
    data = st.session_state.data
    
    if data.empty:
        st.info("分析するデータがありません。「売上入力」からデータを登録してください。")
        return
    
    # 日付を日付型に変換
    data['日付'] = pd.to_datetime(data['日付'])
    
    # 日別推移分析
    with tab1:
        show_daily_trend_analysis(data)
    
    # 曜日分析
    with tab2:
        show_weekday_analysis(data)
    
    # 支払方法分析
    with tab3:
        show_payment_analysis(data)

def show_daily_trend_analysis(data):
    """日別売上推移の分析"""
    st.subheader("日別売上推移")
    
    # 期間選択
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "開始日",
            value=datetime.now().replace(day=1),
            key="trend_start_date"
        )
    with col2:
        end_date = st.date_input(
            "終了日",
            value=datetime.now(),
            key="trend_end_date"
        )
    
    # 日付文字列形式に変換
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # 期間でデータをフィルタリング
    filtered_data = data[
        (data['日付'] >= start_date_str) & 
        (data['日付'] <= end_date_str)
    ].copy()
    
    if filtered_data.empty:
        st.info(f"{start_date_str}から{end_date_str}の期間にデータはありません。")
        return
    
    # 日別集計
    daily_sales = filtered_data.groupby('日付')['売上金額'].sum().reset_index()
    daily_sales['日付文字列'] = daily_sales['日付'].dt.strftime('%Y-%m-%d')
    
    # 7日間の移動平均を計算
    if len(daily_sales) >= 7:
        daily_sales['移動平均 (7日間)'] = daily_sales['売上金額'].rolling(window=7).mean()
    
    # 日別売上グラフ
    fig = go.Figure()
    
    # 棒グラフで売上表示
    fig.add_trace(go.Bar(
        x=daily_sales['日付'],
        y=daily_sales['売上金額'],
        name='日別売上',
        marker_color='#1E88E5',
        hovertemplate='%{x|%Y-%m-%d}<br>売上: ¥%{y:,.0f}<extra></extra>'
    ))
    
    # 移動平均線を追加
    if len(daily_sales) >= 7:
        fig.add_trace(go.Scatter(
            x=daily_sales['日付'],
            y=daily_sales['移動平均 (7日間)'],
            mode='lines',
            name='7日間の移動平均',
            line=dict(width=2, color='#FF5722'),
            hovertemplate='%{x|%Y-%m-%d}<br>移動平均: ¥%{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"{start_date_str}から{end_date_str}までの日別売上推移",
        xaxis_title="日付",
        yaxis_title="売上金額（円）",
        height=500,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 時間帯別の日別推移を表示
    st.subheader("時間帯別推移")
    
    # 時間帯別データの準備
    time_data = filtered_data.groupby(['日付', '時間帯'])['売上金額'].sum().reset_index()
    
    # 昼営業と夜営業のデータを抽出
    lunch_data = time_data[time_data['時間帯'] == '昼営業']
    dinner_data = time_data[time_data['時間帯'] == '夜営業']
    
    # 時間帯別推移グラフ
    fig = go.Figure()
    
    # 昼営業の推移
    fig.add_trace(go.Scatter(
        x=lunch_data['日付'],
        y=lunch_data['売上金額'],
        mode='lines+markers',
        name='昼営業',
        line=dict(color='#1E88E5'),
        marker=dict(size=8),
        hovertemplate='%{x|%Y-%m-%d}<br>昼営業: ¥%{y:,.0f}<extra></extra>'
    ))
    
    # 夜営業の推移
    fig.add_trace(go.Scatter(
        x=dinner_data['日付'],
        y=dinner_data['売上金額'],
        mode='lines+markers',
        name='夜営業',
        line=dict(color='#FFC107'),
        marker=dict(size=8),
        hovertemplate='%{x|%Y-%m-%d}<br>夜営業: ¥%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="時間帯別売上推移",
        xaxis_title="日付",
        yaxis_title="売上金額（円）",
        height=500,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_weekday_analysis(data):
    """曜日別の分析"""
    st.subheader("曜日別売上分析")
    
    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年", range(2020, 2026), index=5, key="weekday_year"
        )
    with col2:
        selected_month = st.selectbox(
            "月", range(1, 13), index=datetime.now().month - 1, key="weekday_month"
        )
    
    # 期間でデータをフィルタリング
    month_start = f"{selected_year}-{selected_month:02d}-01"
    _, last_day = calendar.monthrange(selected_year, selected_month)
    month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"
    
    filtered_data = data[
        (data['日付'] >= month_start) & 
        (data['日付'] <= month_end)
    ].copy()
    
    if filtered_data.empty:
        st.info(f"{selected_year}年{selected_month}月のデータはありません。")
        return
    
    # 曜日情報を追加
    filtered_data['曜日番号'] = filtered_data['日付'].dt.dayofweek
    filtered_data['曜日'] = filtered_data['日付'].dt.dayofweek.map({
        0: '月曜日', 1: '火曜日', 2: '水曜日', 3: '木曜日', 4: '金曜日', 5: '土曜日', 6: '日曜日'
    })
    
    # 曜日別集計
    weekday_sales = filtered_data.groupby('曜日')['売上金額'].sum().reset_index()
    # 曜日順に並び替え
    weekday_order = {
        '月曜日': 0, '火曜日': 1, '水曜日': 2, '木曜日': 3,
        '金曜日': 4, '土曜日': 5, '日曜日': 6
    }
    weekday_sales['order'] = weekday_sales['曜日'].map(weekday_order)
    weekday_sales = weekday_sales.sort_values('order')
    
    # 曜日別の棒グラフ
    fig = px.bar(
        weekday_sales, 
        x='曜日', 
        y='売上金額',
        text_auto='.2s',
        color='曜日',
        color_discrete_map={
            '月曜日': '#9E9E9E', '火曜日': '#9E9E9E', '水曜日': '#9E9E9E', 
            '木曜日': '#9E9E9E', '金曜日': '#64B5F6', 
            '土曜日': '#FFA726', '日曜日': '#EF5350'
        },
        title=f"{selected_year}年{selected_month}月の曜日別売上"
    )
    fig.update_layout(
        xaxis_title="曜日",
        yaxis_title="売上金額（円）",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 時間帯別・曜日別クロス集計
    st.subheader("時間帯・曜日別売上")
    
    # 時間帯・曜日のクロス集計
    cross_data = filtered_data.pivot_table(
        index='曜日', 
        columns='時間帯',
        values='売上金額',
        aggfunc='sum'
    ).reset_index()
    
    # 欠けている列があれば追加
    if '昼営業' not in cross_data.columns:
        cross_data['昼営業'] = 0
    if '夜営業' not in cross_data.columns:
        cross_data['夜営業'] = 0
    
    # 曜日順に並び替え
    cross_data['order'] = cross_data['曜日'].map(weekday_order)
    cross_data = cross_data.sort_values('order')
    
    # 合計列を追加
    cross_data['合計'] = cross_data['昼営業'] + cross_data['夜営業']
    
    # 表示
    st.dataframe(
        cross_data[['曜日', '昼営業', '夜営業', '合計']].style.format({
            '昼営業': '{:,.0f}円',
            '夜営業': '{:,.0f}円',
            '合計': '{:,.0f}円'
        }),
        use_container_width=True,
        hide_index=True
    )

def show_payment_analysis(data):
    """支払方法別の分析"""
    st.subheader("支払方法別売上分析")
    
    # 年月選択
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年", range(2020, 2026), index=5, key="payment_year"
        )
    with col2:
        selected_month = st.selectbox(
            "月", range(1, 13), index=datetime.now().month - 1, key="payment_month"
        )
    
    # 期間でデータをフィルタリング
    month_start = f"{selected_year}-{selected_month:02d}-01"
    _, last_day = calendar.monthrange(selected_year, selected_month)
    month_end = f"{selected_year}-{selected_month:02d}-{last_day:02d}"
    
    filtered_data = data[
        (data['日付'] >= month_start) & 
        (data['日付'] <= month_end)
    ].copy()
    
    if filtered_data.empty:
        st.info(f"{selected_year}年{selected_month}月のデータはありません。")
        return
    
    # 支払方法別集計
    payment_sales = filtered_data.groupby('支払方法')['売上金額'].sum().reset_index()
    
    # データがある場合のみ処理
    if not payment_sales.empty:
        # 支払方法ごとに異なる色を設定
        colors = {
            'cash': '#4CAF50',   # 現金 - 緑
            'card': '#2196F3',   # カード - 青
            'paypay': '#FF5722', # PayPay - オレンジ
            'stella': '#9C27B0', # stella - 紫
            'lunch': '#1E88E5',  # 昼営業 - 青
            'dinner': '#FFC107', # 夜営業 - 黄
            'other': '#757575'   # その他 - グレー
        }
        
        # 支払方法の日本語名
        payment_names = {
            'cash': '現金',
            'card': 'カード',
            'paypay': 'PayPay',
            'stella': 'stella',
            'lunch': '昼営業',
            'dinner': '夜営業',
            'other': 'その他'
        }
        
        # 支払方法に日本語名を追加
        payment_sales['支払方法名'] = payment_sales['支払方法'].map(
            lambda x: payment_names.get(x, x)
        )
        
        # 支払方法別の円グラフ
        fig = px.pie(
            payment_sales,
            values='売上金額',
            names='支払方法名',
            title=f"{selected_year}年{selected_month}月の支払方法別売上",
            color='支払方法名',
            color_discrete_map={
                payment_names.get(k, k): v for k, v in colors.items()
                if payment_names.get(k, k) in payment_sales['支払方法名'].values
            },
            hole=0.3,
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        fig.update_layout(
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 支払方法・時間帯クロス集計
        st.subheader("支払方法・時間帯別売上")
        
        # 支払方法・時間帯のクロス集計
        payment_time_data = filtered_data.pivot_table(
            index='支払方法',
            columns='時間帯',
            values='売上金額',
            aggfunc='sum'
        ).reset_index()
        
        # 欠けている列があれば追加
        if '昼営業' not in payment_time_data.columns:
            payment_time_data['昼営業'] = 0
        if '夜営業' not in payment_time_data.columns:
            payment_time_data['夜営業'] = 0
        
        # 支払方法に日本語名を追加
        payment_time_data['支払方法名'] = payment_time_data['支払方法'].map(
            lambda x: payment_names.get(x, x)
        )
        
        # 合計列を追加
        payment_time_data['合計'] = payment_time_data['昼営業'] + payment_time_data['夜営業']
        
        # 表示
        st.dataframe(
            payment_time_data[['支払方法名', '昼営業', '夜営業', '合計']].style.format({
                '昼営業': '{:,.0f}円',
                '夜営業': '{:,.0f}円',
                '合計': '{:,.0f}円'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("支払方法別のデータがありません。")