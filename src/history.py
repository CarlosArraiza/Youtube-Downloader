import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'history.json')

def load_history() -> list:
    """Carga el historial desde el archivo JSON"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_entry(entry: dict):
    """Añade una entrada al historial"""
    history = load_history()
    history.insert(0, entry)  # más reciente primero
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clear_history():
    """Borra todo el historial"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def build_entry(result: dict) -> dict:
    """Construye una entrada de historial a partir del resultado de una descarga"""
    return {
        'title': result['title'],
        'format': result['format'].upper(),
        'quality': result['quality'],
        'size_mb': result['size_mb'],
        'elapsed_seconds': result['elapsed_seconds'],
        'output_path': result['output_path'],
        'date': datetime.now().strftime('%d/%m/%Y %H:%M')
    }