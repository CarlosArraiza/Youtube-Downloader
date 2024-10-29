import os 
from pytubefix import YouTube

def descargar_video(url):
    try:

        video = YouTube(url)
        stream = video.streams.get_highest_resolution()
        #Obtiene la ruta de descargas del usuario
        # Obtener la ruta de la carpeta de Descargas (intenta con "Descargas" o "Downloads")
        download_path = os.path.join(os.path.expanduser("~"), "Descargas")  # En español
        if not os.path.isdir(download_path):  # Si "Descargas" no existe, prueba con "Downloads"
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        # Muestra información del video
        print(f"Descargando: {video.title}")
        print(f"Resolución: {stream.resolution}")
        
        # Descarga el video en la carpeta actual
        stream.download(output_path=download_path)
        print(f"¡Descarga completada en {download_path}!")
    except Exception as e:
        print("Ocurrió un error:", e)

# Solicita el enlace del video al usuario
url = input("Ingresa la URL del video de YouTube que deseas descargar: ")
descargar_video(url)