from dotenv import load_dotenv
load_dotenv() # Memuat variabel dari .env

import os
import random
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from llm_service import analyze_journal_entry

# --- Konfigurasi Aplikasi dan Database ---
app = Flask(__name__)
DATA_DIR = os.environ.get('RENDER_DISK_PATH', os.path.abspath(os.path.dirname(__file__)))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, 'journal.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Database ---
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

# --- Endpoint Aplikasi ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/analyze_journal', methods=['POST'])
def analyze_api():
    data = request.get_json()
    if not data or 'entry' not in data or 'userId' not in data or 'timeframe' not in data:
        return jsonify({"error": "Data tidak lengkap"}), 400

    current_entry_text = data['entry']
    user_id = data['userId']
    timeframe = data['timeframe']

    previous_entry = None
    user_entries = JournalEntry.query.filter_by(user_id=user_id)
    now = datetime.now(timezone.utc)
    target_time = None

    if timeframe == '1h':
        target_time = now - timedelta(hours=1)
    elif timeframe == '1d':
        target_time = now - timedelta(days=1)

    if target_time:
        previous_entry = user_entries.filter(JournalEntry.created_at >= target_time).order_by(JournalEntry.created_at.desc()).first()
    else:
        entry_count = user_entries.count()
        if entry_count > 0:
            random_offset = random.randint(0, entry_count - 1)
            previous_entry = user_entries.offset(random_offset).first()

    previous_entry_text = previous_entry.content if previous_entry else None
    analysis_result = analyze_journal_entry(current_entry_text, previous_entry_text, timeframe)

    new_entry = JournalEntry(content=current_entry_text, user_id=user_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify(analysis_result)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Mengubah debug mode menjadi False untuk production
    app.run(host='0.0.0.0', port=port, debug=False)