
import streamlit as st
import utils
import google.generativeai as genai

def show():
    # SVG Header
    st.markdown("""
        <div class="custom-svg-header">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 11.5C21.0039 12.8199 20.6957 14.1272 20.1009 15.2967C19.5061 16.4662 18.644 17.4611 17.595 18.1881C16.546 18.915 15.3444 19.3503 14.1027 19.4533C12.861 19.5563 11.6198 19.3235 10.493 18.777L4 21L6.223 14.5C5.67652 13.3732 5.44371 12.132 5.54673 10.8903C5.64975 9.64861 6.08502 8.44702 6.81195 7.39799C7.53888 6.34895 8.53381 5.48685 9.70327 4.89209C10.8727 4.29734 12.1801 3.98906 13.5 3.99304V4.00004H14V4.04304C15.8453 4.11656 17.6009 4.88604 18.8926 6.1873C20.1843 7.48855 20.9168 9.22591 20.934 11.071L21 11.5Z" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2 style="margin: 0; padding: 0; color: #1F2937; font-family: sans-serif;">質疑応答抽出</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption("音声データから質疑応答部分のみを抽出し、要約します。")
    st.divider()

    if not utils.init_gemini():
        st.stop()

    uploaded_file = st.file_uploader(
        "プレゼンテーション音声ファイルをアップロード", 
        type=["mp3", "wav", "m4a", "webm", "txt"]
    )

    if uploaded_file:
        file_ext = uploaded_file.name.lower().split(".")[-1]
        if file_ext in ["mp3", "wav", "m4a", "webm"]:
            st.audio(uploaded_file)
        
        if st.button("AI解析スタート", type="primary"):
            with st.spinner("音声を解析し、質疑応答を抽出しています..."):
                try:
                    file_path = utils.save_audio_file(uploaded_file)
                    
                    model = genai.GenerativeModel(
                        model_name=utils.GEMINI_MODEL,
                        system_instruction=get_qa_prompt()
                    )
                    
                    myfile = genai.upload_file(file_path, mime_type=utils.get_mime_type(file_path))
                    prompt = "この音声ファイルから質疑応答を抽出してください。"
                    response = model.generate_content([myfile, prompt])
                    
                    st.markdown("### 📝 抽出結果")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

def get_qa_prompt():
    return """
役割（Persona）: あなたは、音源データから重要な情報を抽出し、プレゼンテーションと質疑応答を明確に分離する専門家です。

目的（Goal）: ユーザーが提供したプレゼンテーションの音声データから、質疑応答セクションを正確に特定し、汎用的に活用できるように質疑と応答を抽出・整理すること。

指示（Instructions）:
まず、提供された音声データの全体を分析し、プレゼンテーション部分と質疑応答部分を論理的に分離します。
質疑応答セクションを特定したら、以下の手順で情報を抽出してください。
質問と応答をそれぞれ明確に区別し、ペアとしてまとめます。
質問の意図を簡潔に要約します。
応答の内容を要約し、核心的なポイントを抽出します。
抽出した質疑応答は、他のユーザーの学びにもなるよう、汎用的な形式に整理してください。具体的な事例や固有名詞は、一般化できる場合は一般化し、分かりやすい言葉に置き換えることを優先します。

制約（Constraints）:
提供された音声データは、プレゼンテーションと質疑応答の2つの主要なセクションで構成されていることを前提とします。
回答には、具体的な個人の名前や組織名、機密情報を含めないでください。

出力フォーマットの厳守ルール:
- 各質問と応答は必ず1行空けて区切ること
- Markdownの見出しや箇条書きを用いること
- 出力全体を読みやすいブロック構造にすること

出力フォーマット（Output Format）:
抽出した質疑応答は、以下の形式で提供してください。

● 質疑応答のまとめ

【質問1】  
質問の意図を簡潔に要約  

【応答】  
応答の核心的なポイント
"""

show()