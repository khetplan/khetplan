from flask import Flask, jsonify, request, render_template
import sqlite3, json, os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'khetplan.db')
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL, updated_at TEXT NOT NULL)')
        conn.execute('''CREATE TABLE IF NOT EXISTS rain_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rain_type TEXT NOT NULL CHECK(rain_type IN ('light','good','heavy')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )''')


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/api/health')
def health():
    return jsonify(status='ok', app='KhetPlan', database='sqlite')


@app.get('/api/state')
def get_state():
    with db() as conn:
        row = conn.execute('SELECT payload, updated_at FROM app_state WHERE id=1').fetchone()
    if not row:
        return jsonify(state=None, updated_at=None)
    return jsonify(state=json.loads(row['payload']), updated_at=row['updated_at'])


@app.post('/api/state')
def put_state():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Expected a JSON object.'), 400
    if len(json.dumps(payload)) > 900_000:
        return jsonify(error='State is too large.'), 413
    updated_at = datetime.now(timezone.utc).isoformat()
    with db() as conn:
        conn.execute('''INSERT INTO app_state(id, payload, updated_at) VALUES(1, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at''',
                     (json.dumps(payload, ensure_ascii=False), updated_at))
    return jsonify(saved=True, updated_at=updated_at)


@app.get('/api/rain-logs')
def list_rain_logs():
    with db() as conn:
        rows = conn.execute('SELECT id, rain_type, note, created_at FROM rain_logs ORDER BY id DESC LIMIT 50').fetchall()
    return jsonify(logs=[dict(r) for r in rows])


@app.post('/api/rain-logs')
def add_rain_log():
    body = request.get_json(silent=True) or {}
    rain_type = body.get('rain_type')
    note = str(body.get('note', ''))[:500]
    if rain_type not in {'light', 'good', 'heavy'}:
        return jsonify(error="rain_type must be 'light', 'good', or 'heavy'."), 400
    created_at = datetime.now(timezone.utc).isoformat()
    with db() as conn:
        cur = conn.execute('INSERT INTO rain_logs(rain_type, note, created_at) VALUES(?,?,?)', (rain_type, note, created_at))
        log_id = cur.lastrowid
    return jsonify(id=log_id, rain_type=rain_type, note=note, created_at=created_at), 201


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='Request is too large.'), 413


init_db()
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
