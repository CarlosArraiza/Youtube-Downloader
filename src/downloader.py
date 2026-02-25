import yt_dlp
import os

def get_video_info(url: str) -> dict:
    """Obtiene información del vídeo sin descargarlo"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Extraer calidades disponibles
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

def download_video(url: str, quality: str, output_path: str, progress_callback=None) -> bool:
    """Descarga el vídeo en la calidad seleccionada"""
    height = quality.replace('p', '')
    
    def progress_hook(d):
        if d['status'] == 'downloading' and progress_callback:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percentage = (downloaded / total) * 100
                progress_callback(percentage)
        elif d['status'] == 'finished' and progress_callback:
            progress_callback(100)

    ydl_opts = {
        'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error al descargar: {e}")
        return False