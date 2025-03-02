import streamlit as st
import pandas as pd
import base64
from io import StringIO
from datetime import datetime
import calendar
from ..data.loader import save_data, standardize_data

def show_data_management_page():
    """データ管理ページを表示"""
    st.header("データ管理")
    
    # データが空の場合
    if st.session_state.data.empty:
        st.warning("登録されたデータがありません。「売上入力」からデータを登録してください。")
        return
    
    # タブ設定
    tab1, tab2, tab3 = st.tabs(["データ閲覧", "データエクスポート", "データ修復・削除"])
    
    # データ閲覧タブ
    with tab1:
        show_data_view_tab()
    
    # データエクスポートタブ
    with tab2:
        show_data_export_tab()
    
    # データ修復・削除タブ
    with tab3:
        show_data_management_tab()

def show_data_view_tab():
    """データ閲覧タブの表示"""
    st.subheader("売上データ閲覧")
    
    # 期間選択
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        start_year = st.selectbox(
            "開始年", 
            range(2020, 2026), 
            index=5,
            key="view_start_year"
        )
    with col2:
        start_month = st.selectbox(
            "開始月", 
            range(1, 13), 
            index=0,
            key="view_start_month"
        )
    with col3:
        end_year = st.selectbox(
            "終了年", 
            range(2020, 2026), 
            index=5,
            key="view_end_year"
        )
    with col4:
        end_month = st.selectbox(
            "終了月", 
            range(1, 13), 
            index=datetime.now().month - 1,
            key="view_end_month"
        )
    
    # 期間の開始日と終了日
    start_date = f"{start_year}-{start_month:02d}-01"
    
    # 終了月の最終日を計算
    _, last_day = calendar.monthrange(end_year, end_month)
    end_date = f"{end_year}-{end_month:02d}-{last_day:02d}"
    
    # データのフィルタリング
    filtered_data = st.session_state.data[
        (st.session_state.data['日付'] >= start_date) & 
        (st.session_state.data['日付'] <= end_date)
    ].copy()
    
    if filtered_data.empty:
        st.info(f"{start_date}から{end_date}の期間にデータはありません。")
        return
    
    # 列の並び替え
    columns = ["日付", "時間帯", "支払方法", "売上金額", "備考"]
    if all(col in filtered_data.columns for col in columns):
        filtered_data = filtered_data[columns]
    
    # データの整形
    filtered_data = filtered_data.sort_values("日付")
    
    # データテーブルの表示
    st.dataframe(
        filtered_data.style.format({'売上金額': '{:,.0f}円'}),
        use_container_width=True,
        hide_index=True
    )
    
    # データ件数の表示
    st.write(f"表示データ: {len(filtered_data)}件")

def show_data_export_tab():
    """データエクスポートタブの表示"""
    st.subheader("データエクスポート")
    
    # 期間選択
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        start_year = st.selectbox(
            "開始年", 
            range(2020, 2026), 
            index=5,
            key="export_start_year"
        )
    with col2:
        start_month = st.selectbox(
            "開始月", 
            range(1, 13), 
            index=0,
            key="export_start_month"
        )
    with col3:
        end_year = st.selectbox(
            "終了年", 
            range(2020, 2026), 
            index=5,
            key="export_end_year"
        )
    with col4:
        end_month = st.selectbox(
            "終了月", 
            range(1, 13), 
            index=datetime.now().month - 1,
            key="export_end_month"
        )
    
    # 期間の開始日と終了日
    start_date = f"{start_year}-{start_month:02d}-01"
    
    # 終了月の最終日を計算
    _, last_day = calendar.monthrange(end_year, end_month)
    end_date = f"{end_year}-{end_month:02d}-{last_day:02d}"
    
    # データのフィルタリング
    filtered_data = st.session_state.data[
        (st.session_state.data['日付'] >= start_date) & 
        (st.session_state.data['日付'] <= end_date)
    ].copy()
    
    if filtered_data.empty:
        st.info(f"{start_date}から{end_date}の期間にデータはありません。")
        return
    
    # データの整形
    filtered_data = filtered_data.sort_values("日付")
    
    # ダウンロードボタン
    csv = filtered_data.to_csv(index=False).encode('utf-8-sig')
    
    # ダウンロードリンクを作成
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="sales_data_{start_year}{start_month:02d}_to_{end_year}{end_month:02d}.csv">CSVファイルをダウンロード</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # データ件数の表示
    st.write(f"エクスポートデータ: {len(filtered_data)}件")

def show_data_management_tab():
    """データ修復・削除タブの表示"""
    st.subheader("データ修復と削除")
    
    # データ修復
    with st.expander("データ構造を修復"):
        st.info("データの構造に問題がある場合に修復を実行します。")
        if st.button("データ修復を実行"):
            # データを標準化
            st.session_state.data = standardize_data(st.session_state.data)
            # 修復したデータを保存
            save_success = save_data(st.session_state.data)
            if save_success:
                st.success("データ構造の修復が完了しました。")
                st.rerun()
            else:
                st.error("データ修復中にエラーが発生しました。")
    
    # データ削除
    with st.expander("月次データの削除"):
        st.warning("選択した月のデータを削除します。この操作は元に戻せません。")
        
        col1, col2 = st.columns(2)
        with col1:
            delete_year = st.selectbox(
                "年", 
                range(2020, 2026), 
                index=5,
                key="delete_year"
            )
        with col2:
            delete_month = st.selectbox(
                "月", 
                range(1, 13), 
                index=datetime.now().month - 1,
                key="delete_month"
            )
        
        # 削除対象月のデータを確認
        month_start = f"{delete_year}-{delete_month:02d}-01"
        _, last_day = calendar.monthrange(delete_year, delete_month)
        month_end = f"{delete_year}-{delete_month:02d}-{last_day:02d}"
        
        target_data = st.session_state.data[
            (st.session_state.data['日付'] >= month_start) & 
            (st.session_state.data['日付'] <= month_end)
        ]
        
        st.write(f"{delete_year}年{delete_month}月のデータ: {len(target_data)}件")
        
        if not target_data.empty:
            delete_button = st.button(
                f"{delete_year}年{delete_month}月のデータを削除",
                type="primary", 
                key="delete_month_data",
                use_container_width=True
            )
            
            if delete_button:
                # 削除処理
                try:
                    # 選択された月以外のデータを残す
                    mask = ~((st.session_state.data['日付'] >= month_start) &
                             (st.session_state.data['日付'] <= month_end))
                    st.session_state.data = st.session_state.data.loc[mask].copy()
                    
                    # 更新されたデータを保存
                    save_success = save_data(st.session_state.data)
                    if save_success:
                        st.success(f"{delete_year}年{delete_month}月のデータを削除しました。")
                        st.rerun()
                    else:
                        st.error("データの削除中にエラーが発生しました。")
                except Exception as e:
                    st.error(f"データ削除エラー: {e}")
        else:
            st.info(f"{delete_year}年{delete_month}月のデータはありません。")
    
    # 全データ削除
    with st.expander("全データの削除"):
        st.error("全てのデータを削除します。この操作は元に戻せません。")
        
        # 確認用テキスト入力
        confirm_text = st.text_input(
            "確認のため「DELETE ALL DATA」と入力してください",
            key="confirm_delete_all"
        )
        
        if st.button("全データを削除", type="primary", key="delete_all_data", use_container_width=True):
            if confirm_text == "DELETE ALL DATA":
                try:
                    # データフレームを空にする
                    st.session_state.data = pd.DataFrame(columns=["日付", "時間帯", "支払方法", "売上金額", "備考"])
                    
                    # 空のデータを保存
                    save_success = save_data(st.session_state.data)
                    if save_success:
                        st.success("全てのデータを削除しました。")
                        st.rerun()
                    else:
                        st.error("データの削除中にエラーが発生しました。")
                except Exception as e:
                    st.error(f"データ削除エラー: {e}")
            else:
                st.warning("確認テキストが正しくありません。")