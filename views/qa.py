
import streamlit as st
import utils
import google.generativeai as genai

def show():
    st.header("質疑応答抽出")
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
                    
                    myfile = genai.upload_file(file_path)
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