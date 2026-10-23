"""Qt Quick frontend; background jobs communicate through queued Qt signals."""
import os
import sys
import threading
from pathlib import Path
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl, QTimer, Qt
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from config import load_config, save_config, VIDEO_QUALITY_OPTIONS
from downloader import get_video_info, download_video, AUDIO_FORMATS, VIDEO_FORMATS, AUDIO_QUALITIES
from history import load_history, clear_history, build_entry, save_entry
from version import __version__
import updater


class Bridge(QObject):
    changed = Signal()
    infoChanged = Signal()
    settingsChanged = Signal()
    historyChanged = Signal()
    delivered = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.settings = load_config()
        self.info = {}
        self.analyzed_url = ''
        self.cancel = threading.Event()
        self.cancel_update = threading.Event()
        self.update = None
        self.state = dict(settings=self.settings.copy(), history=load_history(), info={},
                          searching=False, downloading=False, progress=0., speed='',
                          status='Pega un enlace para empezar.', error=False,
                          updateState='idle', updateMessage='Busca nuevas versiones cuando quieras.',
                          updateNotes='', updateProgress=0., version=__version__,
                          formats=VIDEO_FORMATS + AUDIO_FORMATS,
                          videoQualities=VIDEO_QUALITY_OPTIONS, audioQualities=AUDIO_QUALITIES)
        self.delivered.connect(self._receive, Qt.ConnectionType.QueuedConnection)

    @Property('QVariantMap', notify=changed)
    def data(self):
        return self.state

    @Property('QVariantMap', notify=infoChanged)
    def videoInfo(self):
        return self.state['info']

    @Property('QVariantMap', notify=settingsChanged)
    def config(self):
        return self.state['settings']

    @Property('QVariantList', notify=historyChanged)
    def entries(self):
        return self.state['history']

    def patch(self, **values):
        self.state.update(values)
        if 'info' in values:
            self.infoChanged.emit()
        if 'settings' in values:
            self.settingsChanged.emit()
        if 'history' in values:
            self.historyChanged.emit()
        self.changed.emit()

    def work(self, kind, function):
        def run():
            try:
                self.delivered.emit(kind, function())
            except Exception as exc:
                self.delivered.emit(kind + 'Error', str(exc))
        threading.Thread(target=run, daemon=True).start()

    @Slot(str, object)
    def _receive(self, kind, result):
        if kind == 'search':
            self.info = result
            self.patch(info=result, searching=False, status='Elige el formato y la calidad.', error=False)
        elif kind == 'searchError':
            self.patch(searching=False, status='No se pudo obtener la información del vídeo: ' + result, error=True)
        elif kind == 'progress':
            p, speed = result
            self.patch(progress=max(0., min(p / 100, 1.)),
                       speed=f'{speed / 1048576:.1f} MB/s' if speed else '',
                       status='Procesando archivo…' if p >= 100 else 'Descargando…')
        elif kind in ('download', 'downloadError'):
            if self.cancel.is_set():
                self.patch(downloading=False, progress=0., speed='', status='Descarga cancelada.', error=False)
            elif kind == 'downloadError' or not result:
                self.patch(downloading=False, speed='', error=True,
                           status='No se pudo completar la descarga.' + (' ' + result if isinstance(result, str) else ''))
            else:
                try:
                    save_entry(build_entry(result))
                    self.patch(history=load_history(), status='Descarga completada.', error=False)
                except OSError as exc:
                    self.patch(status=f'Archivo descargado; no se pudo guardar el historial: {exc}', error=True)
                self.patch(downloading=False, progress=1., speed='')
                if self.settings['open_folder_after_download']:
                    self.openPath(result['output_path'], '')
        elif kind == 'check':
            self.update = result
            self.patch(updateState='available' if result else 'latest',
                       updateMessage=f'Nueva versión disponible: {result["version"]}' if result else f'Tienes la última versión ({__version__}).',
                       updateNotes=result['notes'] if result else '')
        elif kind == 'checkError':
            self.patch(updateState='error', updateMessage='No se pudo buscar actualizaciones: ' + result)
        elif kind == 'updateProgress':
            self.patch(updateProgress=result)
        elif kind == 'install':
            if self.cancel_update.is_set():
                self.patch(updateState='available', updateMessage='Actualización cancelada.')
                return
            try:
                updater.launch_installer(result)
                QApplication.instance().quit()
            except OSError as exc:
                self.patch(updateState='available', updateMessage=f'No se pudo abrir el instalador: {exc}')
        elif kind == 'installError':
            self.patch(updateState='available', updateMessage='Actualización cancelada.' if self.cancel_update.is_set() else result)

    @Slot(str)
    def analyze(self, url):
        if self.state['searching'] or self.state['downloading']:
            return
        url = url.strip()
        if not url.startswith(('https://', 'http://')):
            self.patch(status='Introduce una URL válida de vídeo.', error=True)
            return
        self.info = {}
        self.analyzed_url = url
        self.patch(info={}, searching=True, error=False, progress=0., status='Buscando vídeo…')
        self.work('search', lambda: get_video_info(url))

    @Slot(str, str, str, str)
    def download(self, url, fmt, quality, folder):
        if self.state['downloading']:
            self.cancel.set()
            self.patch(status='Cancelando…')
            return
        if self.state['updateState'] == 'downloading':
            self.patch(status='Espera a que termine la actualización.', error=True)
            return
        if not self.info or url.strip() != self.analyzed_url:
            self.patch(status='Busca este enlace antes de descargar.', error=True)
            return
        if fmt not in VIDEO_FORMATS + AUDIO_FORMATS or not folder.strip() or not quality:
            self.patch(status='Revisa el formato, la calidad y la carpeta.', error=True)
            return
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as exc:
            self.patch(status=f'No se puede utilizar esa carpeta: {exc}', error=True)
            return
        self.cancel.clear()
        self.patch(downloading=True, progress=0., speed='', error=False, status='Iniciando descarga…')
        self.work('download', lambda: download_video(self.analyzed_url, quality, fmt, folder,
                  lambda p, s: self.delivered.emit('progress', (p, s)), self.cancel.is_set))

    @Slot(str, result=str)
    def chooseFolder(self, current):
        return QFileDialog.getExistingDirectory(None, 'Carpeta de descargas', current) or current

    @Slot(str, str)
    def openPath(self, path, fallback):
        target = path if path and os.path.exists(path) else fallback
        if target and os.path.exists(target):
            if os.path.isfile(target) and sys.platform == 'win32':
                import subprocess
                subprocess.Popen(['explorer', '/select,', os.path.normpath(target)])
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(target))
        else:
            self.patch(status='No se encuentra el archivo ni su carpeta.', error=True)

    @Slot('QVariantMap')
    def saveSettings(self, values):
        values = dict(values)
        if values.get('theme') not in ('dark', 'light', 'system'):
            return
        updated = self.settings | values
        try:
            save_config(updated)
            self.settings = updated
            self.patch(settings=updated.copy(), status='Configuración guardada.', error=False)
        except OSError as exc:
            self.patch(status=f'No se pudo guardar la configuración: {exc}', error=True)

    @Slot()
    def clearHistory(self):
        try:
            clear_history()
            self.patch(history=[], status='Historial eliminado. Los archivos se conservan.', error=False)
        except OSError as exc:
            self.patch(status=f'No se pudo limpiar el historial: {exc}', error=True)

    @Slot()
    def checkUpdates(self):
        if self.state['updateState'] in ('checking', 'downloading'):
            return
        self.patch(updateState='checking', updateMessage='Buscando actualizaciones…')
        self.work('check', updater.check_for_update)

    @Slot()
    def installUpdate(self):
        if self.state['updateState'] == 'downloading':
            self.cancel_update.set()
            return
        if not self.update or self.state['downloading']:
            return
        if not updater.is_installed_build():
            QDesktopServices.openUrl(QUrl(self.update['url']))
            return
        self.cancel_update.clear()
        self.patch(updateState='downloading', updateProgress=0., updateMessage='Descargando actualización…')
        self.work('install', lambda: updater.download_installer(self.update,
                  lambda p: self.delivered.emit('updateProgress', p), self.cancel_update.is_set))

    @Slot(result=bool)
    def busy(self):
        return self.state['downloading'] or self.state['updateState'] == 'downloading'

    @Slot()
    def cancelOnClose(self):
        self.cancel.set()
        self.cancel_update.set()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('YouTube Downloader')
    app.setOrganizationName('YouTubeDownloader')
    app.setFont(QFont('Segoe UI', 10))
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    app.setWindowIcon(QIcon(str(root / 'assets' / 'icon.ico')))
    QQuickStyle.setStyle('Basic')
    bridge = Bridge()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('backend', bridge)
    engine.load(QUrl.fromLocalFile(str(root / 'src' / 'qml' / 'Main.qml')))
    if not engine.rootObjects():
        return 1
    if '--smoke-test' in sys.argv:
        QTimer.singleShot(500, app.quit)
    else:
        updater.cleanup_downloads()
        if bridge.settings['check_updates_on_start'] and updater.is_installed_build():
            QTimer.singleShot(3000, bridge.checkUpdates)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
