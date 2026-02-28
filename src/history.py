import json
import os
from datetime import datetime

APP_NAME = "YouTubeDownloader"
DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser("~")), APP_NAME)
os.makedirs(DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_entry(entry: dict):
    history = load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def build_entry(result: dict) -> dict:
    return {
        'title': result['title'],
        'format': result['format'].upper(),
        'quality': result['quality'],
        'size_mb': result['size_mb'],
        'elapsed_seconds': result['elapsed_seconds'],
        'output_path': result['output_path'],
        'file_path': result.get('file_path'),
        'thumbnail_url': result.get('thumbnail_url'),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M')
    }