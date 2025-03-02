import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def display_sales_card(title, value, delta=None, color="#4CAF50", icon="💰"):
    """売上データを表示するカード"""
    container = st.container()
    with container:
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd; background-color: white;">
            <div style="color: gray; font-size: 0.8rem;">{title}</div>
            <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                <div style="font-size: 1.8rem; color: {color}; margin-right: 0.5rem;">{icon}</div>
                <div style="font-size: 1.8rem; font-weight: bold;">¥{value:,.0f}</div>
            </div>
            {f'<div style="color: {"green" if delta > 0 else "red"}; font-size: 0.9rem; margin-top: 0.3rem;">{"↑" if delta > 0 else "↓"} {abs(delta):,.0f} ({abs(delta / value * 100):.1f}%)</div>' if delta is not None else ''}
        </div>
        """, unsafe_allow_html=True)
    return container

def create_sales_bar_chart(data, x, y, title="売上推移", color="#64B5F6", height=400):
    """売上データの棒グラフを作成"""
    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        labels={y: "売上金額（円）"},
        color_discrete_sequence=[color]
    )
    fig.update_layout(
        height=height,
        xaxis_title="",
        yaxis_title="売上金額（円）",
    )
    return fig

def create_sales_line_chart(data, x, y, title="売上推移", color="#4CAF50", height=400):
    """売上データの折れ線グラフを作成"""
    fig = px.line(
        data,
        x=x,
        y=y,
        title=title,
        labels={y: "売上金額（円）"},
        markers=True,
        color_discrete_sequence=[color]
    )
    fig.update_layout(
        height=height,
        xaxis_title="",
        yaxis_title="売上金額（円）",
    )
    return fig

def create_sales_pie_chart(data, values, names, title="売上構成比", height=400):
    """売上データの円グラフを作成"""
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    fig.update_layout(
        height=height
    )
    return fig

def month_selector():
    """年月選択用のセレクトボックスを作成"""
    from datetime import datetime
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "年", range(2020, 2026), index=5
        )
    with col2:
        selected_month = st.selectbox(
            "月", range(1, 13), index=datetime.now().month - 1
        )
    
    return selected_year, selected_month