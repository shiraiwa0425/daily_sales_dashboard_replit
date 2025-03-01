from dailysalesdashboard.main import main
import streamlit as st

if __name__ == "__main__":
    # セッション変数の初期化
    if 'data' not in st.session_state:
        from dailysalesdashboard.utils import load_data
        st.session_state.data = load_data()
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = {}
    if 'previous_year_month' not in st.session_state:
        st.session_state.previous_year_month = ""
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'previous_value' not in st.session_state:
        st.session_state.previous_value = {}
        
    try:
        main()
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())