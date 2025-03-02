import streamlit as st
import pandas as pd
import base64
import os

from .data.loader import load_data, standardize_data
from .pages.data_entry import show_data_entry_page
from .pages.daily_report import show_daily_report_page
from .pages.monthly_report import show_monthly_report_page
from .pages.sales_analysis import show_sales_analysis_page
from .pages.data_management import show_data_management_page

def setup_page():
    """ページの基本設定とスタイルを適用する"""
    st.set_page_config(
        page_title="飲食店売上管理システム",
        page_icon="🍴",
        layout="wide"
    )
    
    # CSSスタイルの追加
    try:
        with open('styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
        .title-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .title-icon {
            height: 3rem;
            margin-right: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

    # ヘッダーとロゴの表示
    svg_url = get_logo_url()
    st.markdown(f"""
    <div class="title-container">
        <img src="{svg_url}" class="title-icon" alt="飲食店アイコン">
        <h1>飲食店売上管理システム</h1>
    </div>
    """, unsafe_allow_html=True)

def get_logo_url():
    """ロゴのURLを取得"""
    try:
        with open('icon.svg', 'r') as f:
            svg_content = f.read()
            b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            return f'data:image/svg+xml;base64,{b64}'
    except FileNotFoundError:
        # シンプルなSVGアイコンを作成
        svg_content = """
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
            <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
            <line x1="6" y1="1" x2="6" y2="4"></line>
            <line x1="10" y1="1" x2="10" y2="4"></line>
            <line x1="14" y1="1" x2="14" y2="4"></line>
        </svg>
        """
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f'data:image/svg+xml;base64,{b64}'

def init_session_state():
    """セッション状態の初期化"""
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = {}
    if 'previous_year_month' not in st.session_state:
        st.session_state.previous_year_month = ""
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'previous_value' not in st.session_state:
        st.session_state.previous_value = {}

def main():
    """メインアプリケーション"""
    # ページ設定とセッション初期化
    setup_page()
    init_session_state()
    
    # サイドバーナビゲーション
    st.sidebar.header("メニュー")
    current_page = st.sidebar.radio(
        label="以下選択",
        options=["売上入力", "日別売上表", "月別売上表", "売上分析", "データ管理"]
    )
    
    # ページ表示
    if current_page == "売上入力":
        show_data_entry_page()
    elif current_page == "日別売上表":
        show_daily_report_page()
    elif current_page == "月別売上表":
        show_monthly_report_page()
    elif current_page == "売上分析":
        show_sales_analysis_page()
    elif current_page == "データ管理":
        show_data_management_page()

if __name__ == "__main__":
    main()
