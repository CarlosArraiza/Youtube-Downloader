import yt_dlp
import os
import time

def get_video_info(url: str) -> dict:
    """Obtiene información del vídeo sin descargarlo"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,  # ignora la playlist, coge solo el vídeo
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
            'formats': formats
        }

def download_video(url: str, quality: str, output_format: str, output_path: str, progress_callback=None) -> dict:
    """
    Descarga el vídeo en la calidad y formato seleccionados.
    Devuelve un dict con info de la descarga o None si falla.
    """
    start_time = time.time()

    if output_format == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality.replace('kbps', ''),
            }],
            'quiet': True,
            'no_warnings': True,
        }
    else:
        height = quality.replace('p', '')
        ydl_opts = {
            'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

    # Guardamos el nombre del archivo descargado
    downloaded_file = []

    def progress_hook(d):
        if d['status'] == 'downloading' and progress_callback:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percentage = (downloaded / total) * 100
                progress_callback(percentage)
        elif d['status'] == 'finished':
            downloaded_file.append(d.get('filename', ''))
            if progress_callback:
                progress_callback(100)

    ydl_opts['progress_hooks'] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Sin título')

        elapsed_time = round(time.time() - start_time, 1)

        # Calcular peso del archivo descargado
        file_size = None
        if output_format == "mp3":
            if downloaded_file:
                filepath = os.path.splitext(downloaded_file[0])[0] + ".mp3"
                if os.path.exists(filepath):
                    file_size = round(os.path.getsize(filepath) / (1024 * 1024), 2)
        else:
            # Para MP4 buscamos el archivo más reciente en la carpeta destino
            try:
                files = [
                    os.path.join(output_path, f)
                    for f in os.listdir(output_path)
                    if f.endswith('.mp4')
                ]
                if files:
                    latest = max(files, key=os.path.getmtime)
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
        }

    except Exception as e:
        print(f"Error al descargar: {e}")
        return None