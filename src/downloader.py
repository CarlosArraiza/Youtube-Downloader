import yt_dlp
import os
import time
import sys

# Formatos de audio soportados
AUDIO_FORMATS = ["mp3", "aac", "flac", "ogg", "wav", "m4a"]

# Formatos de vídeo soportados
VIDEO_FORMATS = ["mp4", "mkv", "avi", "webm", "mov"]

# Calidades de audio disponibles
AUDIO_QUALITIES = ["320kbps", "192kbps", "128kbps"]

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.join(os.path.dirname(__file__), '..')

    ffmpeg = os.path.join(base_path, 'ffmpeg.exe')
    if os.path.exists(ffmpeg):
        return base_path
    return None


def get_video_info(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get('_type') == 'playlist':
            raise ValueError("Las URLs de playlist no están soportadas. Pega la URL de un vídeo individual.")
        formats = []
        seen = set()
        for f in info.get('formats', []):
            height = f.get('height')
            if height and f.get('vcodec') != 'none':
                label = f"{height}p"
                if label not in seen:
                    seen.add(label)
                    formats.append(label)
        formats.sort(key=lambda x: int(x[:-1]), reverse=True)
        return {
            'title': info.get('title', 'Sin título'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader') or info.get('channel', 'Desconocido'),
            'formats': formats,
        }


def download_video(url: str, quality: str, output_format: str, output_path: str,
                   progress_callback=None, cancel_check=None) -> dict:
    start_time = time.time()
    output_format = output_format.lower()

    ffmpeg_location = get_ffmpeg_path()

    if output_format in AUDIO_FORMATS:
        codec_map = {
            'mp3':  ('mp3',    quality.replace('kbps', '')),
            'aac':  ('aac',    quality.replace('kbps', '')),
            'flac': ('flac',   '0'),
            'ogg':  ('vorbis', quality.replace('kbps', '')),
            'wav':  ('wav',    '0'),
            'm4a':  ('m4a',    quality.replace('kbps', '')),
        }
        codec, q = codec_map[output_format]
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': q,
            }],
            'quiet': True,
            'no_warnings': True,
        }
        if ffmpeg_location:
            ydl_opts['ffmpeg_location'] = ffmpeg_location
    else:
        height = quality.replace('p', '')
        format_map = {
            'mp4':  (f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best', 'mp4'),
            'mkv':  (f'bestvideo[height<={height}]+bestaudio/best', 'mkv'),
            'avi':  (f'bestvideo[height<={height}]+bestaudio/best', 'avi'),
            'webm': (f'bestvideo[height<={height}][ext=webm]+bestaudio[ext=webm]/bestvideo[height<={height}]+bestaudio/best', 'webm'),
            'mov':  (f'bestvideo[height<={height}]+bestaudio/best', 'mov'),
        }
        fmt_selector, merge_fmt = format_map.get(output_format, (f'bestvideo[height<={height}]+bestaudio/best', output_format))
        ydl_opts = {
            'format': fmt_selector,
            'noplaylist': True,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': merge_fmt,
            'quiet': True,
            'no_warnings': True,
        }
        if ffmpeg_location:
            ydl_opts['ffmpeg_location'] = ffmpeg_location

    downloaded_file = []
    thumbnail_url = [None]

    def progress_hook(d):
        if cancel_check and cancel_check():
            raise Exception("Descarga cancelada por el usuario")
        if d['status'] == 'downloading' and progress_callback:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0) or 0
            if total > 0:
                percentage = (downloaded / total) * 100
                progress_callback(percentage, speed)
        elif d['status'] == 'finished':
            downloaded_file.append(d.get('filename', ''))
            if progress_callback:
                progress_callback(100, 0)

    ydl_opts['progress_hooks'] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Sin título')
            thumbnail_url[0] = info.get('thumbnail', '')

        elapsed_time = round(time.time() - start_time, 1)
        file_path = None
        file_size = None

        if output_format in AUDIO_FORMATS:
            if downloaded_file:
                candidate = os.path.splitext(downloaded_file[0])[0] + f".{output_format}"
                if os.path.exists(candidate):
                    file_path = candidate
                    file_size = round(os.path.getsize(candidate) / (1024 * 1024), 2)
        else:
            try:
                files = [
                    os.path.join(output_path, f)
                    for f in os.listdir(output_path)
                    if f.endswith(f'.{output_format}')
                ]
                if files:
                    latest = max(files, key=os.path.getmtime)
                    file_path = latest
                    file_size = round(os.path.getsize(latest) / (1024 * 1024), 2)
            except Exception:
                pass

        return {
            'title': title,
            'format': output_format,
            'quality': quality,
            'size_mb': file_size,
            'elapsed_seconds': elapsed_time,
            'output_path': output_path,
            'file_path': file_path,
            'thumbnail_url': thumbnail_url[0],
        }

    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg or "bot" in error_msg:
            print("Error: Este vídeo requiere estar logueado en YouTube.")
        elif "cancelada" in error_msg:
            raise
        else:
            print(f"Error al descargar: {e}")
        return None