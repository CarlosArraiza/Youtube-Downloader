import json
import os

APP_NAME = "YouTubeDownloader"
DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser("~")), APP_NAME)
os.makedirs(DATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

VIDEO_QUALITY_OPTIONS = ["Mejor disponible", "2160p", "1440p", "1080p", "720p", "480p", "360p", "144p"]

DEFAULTS = {
    'open_folder_after_download': False,
    'default_output_path': os.path.join(os.path.expanduser("~"), "Downloads"),
    'theme': 'dark',
    'default_format': 'mp4',
    'default_quality_video': 'Mejor disponible',
    'default_quality_audio': '320kbps',
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return DEFAULTS.copy()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for key, value in DEFAULTS.items():
            data.setdefault(key, value)
        return data
    except Exception:
        return DEFAULTS.copy()


def save_config(config: dict):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)