import os
from pytubefix import YouTube

def descargar_video(url, solo_audio=False):
    try:
        # Crea una instancia de YouTube con la URL proporcionada
        video = YouTube(url)
        
        if solo_audio:
            # Selecciona el stream de solo audio
            stream = video.streams.filter(only_audio=True).first()
            print(f"Descargando solo el audio de: {video.title}")
        else:
            # Selecciona el stream de video con la mayor resolución
            stream = video.streams.get_highest_resolution()
            print(f"Descargando video completo de: {video.title}")
            print(f"Resolución: {stream.resolution}")
        
        # Obtiene la ruta de descargas del usuario
        download_path = os.path.join(os.path.expanduser("~"), "Descargas")  # En español
        if not os.path.isdir(download_path):  # Si "Descargas" no existe, prueba con "Downloads"
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Descarga el archivo
        stream.download(output_path=download_path)
        
        if solo_audio:
            # Cambia la extensión a .mp3 para el archivo de solo audio
            original_file = os.path.join(download_path, stream.default_filename)
            base, ext = os.path.splitext(original_file)
            new_file = f"{base}.mp3"
            os.rename(original_file, new_file)
            print(f"¡Descarga de audio completada en {new_file}!")
        else:
            print(f"¡Descarga de video completada en {download_path}!")
    
    except Exception as e:
        print("Ocurrió un error:", e)

# Solicita el enlace del video al usuario
url = input("Ingresa la URL del video de YouTube que deseas descargar: ")
opcion = input("¿Quieres descargar solo el audio? (s/n): ").strip().lower()

# Llama a la función con la opción elegida
descargar_video(url, solo_audio=(opcion == 's'))
