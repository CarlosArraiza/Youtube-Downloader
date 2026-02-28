# YouTube Downloader 📹

Herramienta de escritorio para descargar vídeos y audio de YouTube con interfaz gráfica moderna. Desarrollada con Python, CustomTkinter y yt-dlp.

## Características ✨

- **Interfaz gráfica moderna** en modo oscuro (CustomTkinter)
- **Múltiples formatos de vídeo**: MP4, MKV, AVI, WEBM, MOV
- **Múltiples formatos de audio**: MP3, AAC, FLAC, OGG, WAV, M4A
- **Selector de calidad dinámico**: detecta automáticamente las resoluciones disponibles del vídeo (1080p, 720p, 480p...) y selecciona la mejor por defecto
- **Calidad de audio**: 320kbps seleccionado por defecto (también disponible 192kbps y 128kbps)
- **Barra de progreso** con velocidad de descarga en tiempo real
- **Botón cancelar** para interrumpir la descarga en cualquier momento
- **Historial de descargas** con título, fecha, formato, calidad, tamaño y carpeta de destino
- **Selector de carpeta de destino** personalizable (por defecto, la carpeta Descargas del usuario)
- **Compatible con Windows**, macOS y Linux
- **Ejecutable `.exe`** disponible para Windows sin necesidad de instalar Python

## Capturas de pantalla

> Pestaña de descarga y pestaña de historial.

## Instalación ⚙️

### Opción 1 — Ejecutable (recomendado para Windows)

Descarga el archivo `.exe` desde la carpeta `dist/` y ejecútalo directamente. No requiere instalar nada.

### Opción 2 — Desde el código fuente

#### 1. Clona el repositorio

```bash
git clone https://github.com/CarlosArraiza/Youtube-Downloader.git
cd Youtube-Downloader
```

#### 2. Crea un entorno virtual y actívalo

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS / Linux:
```bash
source venv/bin/activate
```

#### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

#### 4. Ejecuta la aplicación

```bash
python src/gui.py
```

## Uso 🚀

1. Pega la URL del vídeo de YouTube en el campo de texto
2. Pulsa **Buscar** para obtener la información del vídeo
3. Selecciona el **formato** (vídeo o audio) y la **calidad** deseada
4. Elige la **carpeta de destino** (por defecto, tu carpeta Descargas)
5. Pulsa **Descargar**
6. Puedes cancelar la descarga en cualquier momento con el botón **Cancelar**

## Requisitos 🔧

- Python 3.8 o superior
- ffmpeg (incluido en el `.exe`; si ejecutas desde código, debe estar en el PATH o en la carpeta raíz del proyecto)
- Conexión a Internet

## Dependencias principales

| Paquete | Uso |
|---|---|
| yt-dlp | Motor de descarga |
| customtkinter | Interfaz gráfica |
| ffmpeg | Conversión y mezcla de formatos |

## Estructura del proyecto

```
Youtube-Downloader/
├── src/
│   ├── gui.py          # Interfaz gráfica
│   ├── downloader.py   # Lógica de descarga
│   └── history.py      # Gestión del historial
├── assets/
│   └── icon.ico        # Icono de la aplicación
├── dist/               # Ejecutable .exe
├── requirements.txt
└── README.md
```

## Licencia 📄

Este proyecto está bajo la licencia MIT.