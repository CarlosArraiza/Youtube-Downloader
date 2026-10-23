# YouTube Downloader 📹

Herramienta de escritorio para descargar vídeos y audio de YouTube con interfaz gráfica moderna. Desarrollada con Python, PySide6 / Qt Quick y yt-dlp.

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
- **Diseño Esencial**: ventana redimensionable, navegación superior y acento azul consistente en ambos temas

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
- **Buscar actualizaciones al iniciar**: activado por defecto; las novedades se muestran en Acerca de
- Configuración guardada en `%LOCALAPPDATA%\YouTubeDownloader\config.json`

### Acerca de y actualizaciones
- **Versión instalada** y enlace al repositorio
- **Buscar actualizaciones**: consulta las releases de GitHub y muestra las novedades de la versión nueva
- **Descargar e instalar**: descarga el instalador con barra de progreso, comprueba su huella SHA-256 con la publicada en GitHub, lo ejecuta (Windows pide permisos de administrador) y la app se vuelve a abrir ya actualizada. La configuración y el historial se conservan

## Instalación ⚙️

### Opción 1 — Instalador (recomendado para Windows)

Descarga `YouTubeDownloader-Setup-vX.Y.Z.exe` de la última [release](https://github.com/cali-sb/Youtube-Downloader/releases) y ejecútalo. No requiere instalar Python ni dependencias. A partir de la 0.8.0 la app se actualiza sola desde **Acerca de**.

### Opción 2 — Desde el código fuente

#### 1. Clona el repositorio

```bash
git clone https://github.com/cali-sb/Youtube-Downloader.git
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

## Compilar y publicar una versión 📦

La versión está solo en `src/version.py`; el `.spec` de PyInstaller y el instalador la toman de ahí.

1. Cambia `__version__` en `src/version.py`.
2. Ejecuta las pruebas (`.\venv\Scripts\python.exe -m unittest discover -s tests -v`) y `.\build.ps1` (necesita PyInstaller en el `venv`, [Inno Setup 6](https://jrsoftware.org/isinfo.php) y ffmpeg en `C:\ffmpeg\bin`). Deja el instalador en `installer_output\`.
3. Crea una release en GitHub con la etiqueta de la versión (p. ej. `1.0.0`) y adjunta `YouTubeDownloader-Setup-vX.Y.Z.exe`. El nombre del fichero tiene que contener `Setup` y acabar en `.exe` para que la app lo encuentre.

## Uso 🚀

1. Pega la URL del vídeo de YouTube en el campo de texto
2. Pulsa **Buscar** para obtener la información y miniatura del vídeo
3. Selecciona el **formato** y la **calidad** deseada
4. Elige la **carpeta de destino**
5. Pulsa **Descargar**
6. Puedes cancelar en cualquier momento con el botón **Cancelar**

## Requisitos 🔧

- Windows 10/11 de 64 bits para el instalador
- Desde código: desarrollada y probada con Python 3.13, PySide6 6.12 y PyInstaller 6.19
- ffmpeg (el instalador lo incluye en la carpeta de la app; si ejecutas desde código debe estar en el PATH o en la raíz del proyecto)
- Conexión a Internet

## Dependencias principales

| Paquete | Uso |
|---|---|
| yt-dlp | Motor de descarga |
| PySide6 (Qt Quick / QML) | Interfaz gráfica |
| Pillow | Regenerar el icono (`create_icon.py`) |
| requests | Descarga de miniaturas y de actualizaciones |
| packaging | Comparación de versiones |
| ffmpeg | Conversión y mezcla de formatos |

## Estructura del proyecto

```
Youtube-Downloader/
├── src/
│   ├── qt_gui.py       # Puente Python ↔ QML y arranque de la app
│   ├── qml/Main.qml    # Interfaz (Qt Quick)
│   ├── gui.py          # Entrada de compatibilidad (remite a qt_gui)
│   ├── downloader.py   # Lógica de descarga
│   ├── history.py      # Gestión del historial
│   ├── config.py       # Gestión de configuración
│   ├── updater.py      # Búsqueda e instalación de actualizaciones
│   └── version.py      # Versión de la app (única fuente)
├── assets/
│   └── icon.ico        # Icono de la aplicación
├── tests/              # Pruebas de la interfaz (unittest, sin conexión)
├── create_icon.py      # Script para regenerar el icono
├── YouTubeDownloader.spec  # Empaquetado PyInstaller (carpeta, no un solo .exe)
├── installer.iss       # Instalador de Inno Setup
├── build.ps1           # Compila la app y el instalador
├── main.py             # Punto de entrada
├── requirements.txt
└── README.md
```
