# YouTube Downloader 📹

Herramienta de escritorio para descargar vídeos y audio de YouTube con interfaz gráfica moderna. Desarrollada con Python, CustomTkinter y yt-dlp.

## Capturas de pantalla

> Tema oscuro y tema claro disponibles.

## Características ✨

### Descarga
- **Múltiples formatos de vídeo**: MP4, MKV, AVI, WEBM, MOV
- **Múltiples formatos de audio**: MP3, AAC, FLAC, OGG, WAV, M4A
- **Selector de calidad dinámico**: detecta automáticamente las resoluciones disponibles del vídeo
- **Calidad de audio**: hasta 320kbps
- **Barra de progreso** con velocidad de descarga en tiempo real
- **Botón cancelar** para interrumpir la descarga en cualquier momento

### Interfaz
- **Interfaz gráfica moderna** con tema oscuro y claro (modo sistema también disponible)
- **Miniatura del vídeo** mostrada al buscar (formato 16:9, sin franjas negras)
- **Información del vídeo**: título, canal, duración y calidades disponibles
- **Animación de búsqueda** mientras se obtiene la información del vídeo
- **Colores YouTube**: botones rojos en tema claro, azules en tema oscuro

### Historial
- **Historial de descargas** con título, canal, fecha, formato, calidad, tamaño y carpeta
- **Miniaturas en el historial** cargadas desde URL
- **Botón "📂 Abrir"** en cada entrada para localizar el archivo en el explorador (selecciona el archivo directamente)
- **Limpiar historial** con confirmación

### Configuración
- **Abrir carpeta al terminar**: abre automáticamente el explorador al completar una descarga
- **Carpeta de descarga por defecto**: personalizable con selector de carpeta
- **Tema**: Oscuro / Claro / Sistema (cambio en caliente sin reiniciar)
- **Formato por defecto**: selecciona el formato que se usará al abrir la app
- **Calidad de vídeo por defecto**: desde 144p hasta 2160p, o mejor disponible
- **Calidad de audio por defecto**: 128kbps, 192kbps o 320kbps
- Configuración guardada en `%LOCALAPPDATA%\YouTubeDownloader\config.json`

## Instalación ⚙️

### Opción 1 — Ejecutable (recomendado para Windows)

Descarga el archivo `.exe` desde la carpeta `dist/` y ejecútalo directamente. No requiere instalar Python ni dependencias.

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
python main.py
```

## Uso 🚀

1. Pega la URL del vídeo de YouTube en el campo de texto
2. Pulsa **Buscar** para obtener la información y miniatura del vídeo
3. Selecciona el **formato** y la **calidad** deseada
4. Elige la **carpeta de destino**
5. Pulsa **Descargar**
6. Puedes cancelar en cualquier momento con el botón **Cancelar**

## Requisitos 🔧

- Python 3.8 o superior
- ffmpeg (incluido en el `.exe`; si ejecutas desde código debe estar en el PATH o en la raíz del proyecto)
- Conexión a Internet

## Dependencias principales

| Paquete | Uso |
|---|---|
| yt-dlp | Motor de descarga |
| customtkinter | Interfaz gráfica |
| Pillow | Procesamiento de miniaturas |
| requests | Descarga de miniaturas desde URL |
| ffmpeg | Conversión y mezcla de formatos |

## Estructura del proyecto

```
Youtube-Downloader/
├── src/
│   ├── gui.py          # Interfaz gráfica
│   ├── downloader.py   # Lógica de descarga
│   ├── history.py      # Gestión del historial
│   └── config.py       # Gestión de configuración
├── assets/
│   ├── icon.ico        # Icono de la aplicación
│   └── create_icon.py  # Script para regenerar el icono
├── dist/               # Ejecutable .exe
├── main.py             # Punto de entrada
├── requirements.txt
└── README.md
```

## Licencia 📄

Este proyecto está bajo la licencia MIT.