import json
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)
BASE = Path(__file__).resolve().parent
STATE_FILE = Path(os.getenv('DISPLAY_STATE_FILE', BASE / 'display_state.example.json'))
STALE_SECONDS = int(os.getenv('DISPLAY_STALE_SECONDS', '900'))


def load_state():
    with STATE_FILE.open('r', encoding='utf-8') as f:
        data = json.load(f)
    required = {'schema_version','system_status','threat_level','p0_alerts','source_health','brief_status','top_signal','watch_domains'}
    missing = required - data.keys()
    if missing:
        raise ValueError('Missing DisplayState fields: ' + ', '.join(sorted(missing)))
    generated = data.get('generated_at')
    if generated:
        dt = datetime.fromisoformat(generated.replace('Z', '+00:00'))
        age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
        data['stale'] = age > STALE_SECONDS
        if data['stale'] and data.get('brief_status') == 'READY':
            data['brief_status'] = 'STALE'
    else:
        data['generated_at'] = datetime.now(timezone.utc).isoformat()
        data['stale'] = True
    return data


@app.get('/healthz')
def health():
    try:
        load_state()
        return jsonify({'status':'ok','service':'nura-display-state'}), 200
    except Exception as exc:
        return jsonify({'status':'error','error':str(exc)}), 503


@app.get('/api/v1/display-state')
def display_state():
    try:
        response = jsonify(load_state())
        response.headers['Cache-Control'] = 'no-store'
        return response
    except Exception as exc:
        return jsonify({'error':'display_state_unavailable','detail':str(exc)}), 503


@app.get('/')
def index():
    return send_from_directory(BASE / 'web', 'index.html')


if __name__ == '__main__':
    app.run(host=os.getenv('DISPLAY_BIND','127.0.0.1'), port=int(os.getenv('DISPLAY_PORT','8787')))
