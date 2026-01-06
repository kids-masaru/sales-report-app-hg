
import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from utils import (
    process_audio_only, process_text_only, process_audio_and_text,
    upload_file_to_kintone, upload_to_kintone, save_audio_file,
    STAFF_OPTIONS, SALES_ACTIVITY_OPTIONS, NEXT_SALES_ACTIVITY_OPTIONS, init_gemini, search_clients, calculate_smart_next_date
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

# --- Configuration ---
# Password from env
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
UPLOAD_FOLDER = 'saved_audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Routes ---

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.before_request
def check_auth():
    # Allow static resources to be served without login (for icon loading on iOS)
    if request.endpoint == 'serve_static':
        return
    if request.endpoint == 'login':
        return
    if APP_PASSWORD and not session.get('authenticated'):
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == APP_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash('パスワードが違います', 'error')
            flash('パスワードが違います', 'error')
    return render_template('login.html')

@app.route('/api/search_clients', methods=['GET'])
def search_clients_route():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify([])
    results = search_clients(keyword)
    return jsonify(results)

@app.route('/', methods=['GET'])
def index():
    # Trying root-relative without /app prefix which was HF specific.
    # Bump version to 13
    icon_url = "/static/icon.png?v=13" 
    ios_icon_url = "/static/apple-touch-icon.png?v=13" 
    manifest_url = "/static/manifest.json?v=13"
    
    return render_template('index.html', staff_options=STAFF_OPTIONS)

@app.route('/process', methods=['POST'])
def process():
    if not init_gemini():
        flash('Gemini APIの設定エラーが発生しました', 'error')
        return redirect(url_for('index'))

    text_input = request.form.get('text_input', '').strip()
    audio_file = request.files.get('audio_file')
    staff_name = request.form.get('staff_name')
    client_id = request.form.get('client_id', '')
    client_name = request.form.get('client_name', '')
    mode = request.form.get('mode', 'sales') # sales or qa

    if not audio_file and not text_input:
        flash('音声ファイルまたはテキストを入力してください', 'error')
        return redirect(url_for('index'))

    saved_path = None
    try:
        data = {}
        if audio_file and audio_file.filename != '':
            # Save file
            saved_path = save_audio_file(audio_file)
            
            if text_input:
                data = process_audio_and_text(saved_path, text_input, mode)
            else:
                data = process_audio_only(saved_path, mode)
        elif text_input:
            data = process_text_only(text_input, mode)

        if not data:
            flash('AIによる抽出に失敗しました', 'error')
            return redirect(url_for('index'))
         
        # Inject client info if available
        if client_id:
            data['取引先ID'] = client_id
            data['取引先名'] = client_name # For display
            
        # Ensure Next Proposal Date is filled (Default: 3 days later, skip weekends)
        # Ensure Next Proposal Date is filled (Default: 3 days later, skip weekends)
        # Only for Sales Report mode
        if mode != 'qa' and not data.get('次回提案予定日'):
            data['次回提案予定日'] = calculate_smart_next_date(data.get('対応日'))
            
        # Success -> Confirm Page
        return render_template('confirm.html', data=data, file_path=saved_path or "", staff_name=staff_name, sales_options=SALES_ACTIVITY_OPTIONS, next_sales_options=NEXT_SALES_ACTIVITY_OPTIONS, staff_options=STAFF_OPTIONS, mode=mode)

    except Exception as e:
        flash(f"エラーが発生しました: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save():
    # Gather data from form
    form_data = request.form.to_dict()
    file_path = form_data.pop('file_path', '')
    staff_name = form_data.pop('staff_name', '')
    
    # Reconstruct data dict for kintone
    data = form_data
    # Add staff info if needed by utils (it is, see utils.py:264)
    data['対応者'] = staff_name

    file_keys = []
    if file_path and os.path.exists(file_path):
        fk = upload_file_to_kintone(file_path, os.path.basename(file_path))
        if fk:
            file_keys.append(fk)
    
    success, error_msg = upload_to_kintone(data, file_keys)
    
    if success:
        flash('Kintoneに正常に登録されました！', 'success')
    else:
        # User-friendly error message if possible, but raw details are better for debugging now
        flash(f'Kintoneへの登録に失敗しました: {error_msg}', 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # For local dev
    app.run(debug=True, port=8501, host='0.0.0.0')
