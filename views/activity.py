
import streamlit as st
import utils
from datetime import date, timedelta

def show():
    # SVG Header
    st.markdown("""
        <div class="custom-svg-header">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 13H8" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 17H8" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 9H8" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2 style="margin: 0; padding: 0; color: #1F2937; font-family: sans-serif;">活動記録</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if not utils.init_gemini():
        st.stop()

    # Success Screen
    if st.session_state.get("submission_success"):
        st.success("Kintoneへの登録が完了しました！🎉")
        st.balloons()
        st.info("データは正常に保存されました。続けて新しい記録を作成できます。")
        
        if st.button("続けて新しい記録を作成する", type="primary"):
            st.session_state.submission_success = False
            st.session_state.extracted_data = None
            st.session_state.client_results = []
            st.session_state.selected_client = None
            st.session_state.uploaded_file_path = None
            st.session_state.uploaded_file_name = None
            st.rerun()
        return

    # STEP 1: Basic Settings
    query_params = st.query_params
    saved_staff = query_params.get("staff", utils.STAFF_OPTIONS[0])
    if saved_staff not in utils.STAFF_OPTIONS: saved_staff = utils.STAFF_OPTIONS[0]
    default_staff_index = utils.STAFF_OPTIONS.index(saved_staff)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        staff = st.selectbox("対応者", options=utils.STAFF_OPTIONS, index=default_staff_index, label_visibility="collapsed")
        if staff != saved_staff:
            st.query_params["staff"] = staff
    
    with col2:
        client_search = st.text_input("取引先検索", placeholder="会社名を入力...", label_visibility="collapsed")
    
    # Advanced Staff Info (Optional)
    with st.expander("担当者詳細入力（必要な場合のみ）"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            staff_dept = st.text_input("担当者部署", placeholder="例: 営業部")
        with col_s2:
            staff_name = st.text_input("担当者名", placeholder="例: 田中 太郎")
            
    if "client_results" not in st.session_state: st.session_state.client_results = []
    if "selected_client" not in st.session_state: st.session_state.selected_client = None
    
    if client_search:
        st.session_state.client_results = utils.search_clients(client_search)
    
    if st.session_state.client_results:
        client_options = {f"{c['name']}": c for c in st.session_state.client_results}
        selected_name = st.selectbox("取引先を選択", options=list(client_options.keys()), label_visibility="collapsed")
        if selected_name:
            st.session_state.selected_client = client_options[selected_name]
    else:
        if st.session_state.selected_client:
             st.info(f"選択中: {st.session_state.selected_client['name']}")
        elif client_search:
             st.caption("見つかりませんでした")

    # STEP 2: Report Content
    tab1, tab2 = st.tabs(["音声/ファイル", "テキスト直接入力"])
    
    with tab1:
        uploaded_file = st.file_uploader("ファイルをアップロード", type=["mp3", "wav", "m4a", "webm", "txt"], label_visibility="collapsed")
    with tab2:
        text_input = st.text_area("テキストメモ", height=100, placeholder="商談内容を入力...", label_visibility="collapsed")

    if st.button("AI解析スタート", type="primary"):
        if not st.session_state.selected_client:
            st.warning("取引先を選択してください")
            st.stop()
            
        with st.spinner("解析中..."):
            extracted_data = None
            saved_file_path = None
            is_audio = False
            file_content_txt = ""
            
            if uploaded_file:
                file_ext = uploaded_file.name.lower().split(".")[-1]
                if file_ext in ["mp3", "wav", "m4a", "webm"]:
                    is_audio = True
                    saved_file_path = utils.save_audio_file(uploaded_file)
                elif file_ext == "txt":
                    file_content_txt = uploaded_file.read().decode("utf-8")
            
            if is_audio and saved_file_path:
                if text_input:
                    extracted_data = utils.process_audio_and_text(saved_file_path, text_input)
                else:
                    extracted_data = utils.process_audio_only(saved_file_path)
            else:
                combined_text = (file_content_txt + "\n" + text_input).strip()
                if combined_text:
                    extracted_data = utils.process_text_only(combined_text)
            
            if extracted_data:
                extracted_data["取引先ID"] = st.session_state.selected_client["id"]
                extracted_data["取引先名"] = st.session_state.selected_client["name"]
                extracted_data["対応者"] = staff
                # 担当者詳細があれば商談内容の先頭に追記
                staff_info_str = ""
                if staff_dept: staff_info_str += f"{staff_dept} "
                if staff_name: staff_info_str += f"{staff_name}様"
                
                if staff_info_str:
                    current_content = extracted_data.get("商談内容", "")
                    extracted_data["商談内容"] = f"{staff_info_str}\n{current_content}"

                st.session_state.uploaded_file_path = saved_file_path
                st.session_state.uploaded_file_name = uploaded_file.name if uploaded_file else None
                st.session_state.extracted_data = extracted_data
                st.rerun()

    # STEP 3: Edit & Submit
    if "extracted_data" in st.session_state and st.session_state.extracted_data:
        data = st.session_state.extracted_data
        st.markdown("---")
        st.subheader("内容確認・修正")
        
        col1, col2 = st.columns(2)
        with col1:
            default_date = utils.convert_date_str_safe(data.get("対応日"), lambda: date.today())
            data["対応日"] = st.date_input("対応日", value=default_date).strftime("%Y-%m-%d")
            ai_activity = data.get("新規営業件名", "架電、メール")
            idx = utils.SALES_ACTIVITY_OPTIONS.index(ai_activity) if ai_activity in utils.SALES_ACTIVITY_OPTIONS else 0
            data["新規営業件名"] = st.selectbox("新規営業件名", options=utils.SALES_ACTIVITY_OPTIONS, index=idx)
            
        with col2:
            default_next_date = utils.convert_date_str_safe(data.get("次回提案予定日"), lambda: date.today() + timedelta(days=7))
            data["次回提案予定日"] = st.date_input("次回予定日", value=default_next_date).strftime("%Y-%m-%d")
            ai_next_activity = data.get("次回営業件名", "架電、メール")
            idx_next = utils.SALES_ACTIVITY_OPTIONS.index(ai_next_activity) if ai_next_activity in utils.SALES_ACTIVITY_OPTIONS else 0
            data["次回営業件名"] = st.selectbox("次回営業件名", options=utils.SALES_ACTIVITY_OPTIONS, index=idx_next)

        data["商談内容"] = st.text_area("商談内容", value=data.get("商談内容", ""), height=150)
        data["現在の課題・問題点"] = st.text_area("現在の課題", value=data.get("現在の課題・問題点", ""), height=80)
        data["競合・マーケット情報"] = st.text_area("競合情報", value=data.get("競合・マーケット情報", ""), height=80)
        data["次回提案内容"] = st.text_area("次回提案", value=data.get("次回提案内容", ""), height=60)
        
        if st.button("送信 (Kintoneへ) 🚀", type="primary"):
            with st.spinner("送信中..."):
                file_keys = []
                path = st.session_state.get("uploaded_file_path")
                name = st.session_state.get("uploaded_file_name")
                if path and name:
                     fk = utils.upload_file_to_kintone(path, name)
                     if fk: file_keys.append(fk)
                if utils.upload_to_kintone(data, file_keys):
                    st.session_state.submission_success = True
                    st.rerun()

show()