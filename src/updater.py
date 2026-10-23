import hashlib
import os
import re
import sys
import tempfile

import requests
from packaging.version import InvalidVersion, Version

from version import __version__

REPO = "CarlosArraiza/Youtube-Downloader"
REPO_URL = f"https://github.com/{REPO}"
RELEASES_API = f"https://api.github.com/repos/{REPO}/releases"
INSTALLER_RE = re.compile(r"Setup.*\.exe$", re.IGNORECASE)
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "YouTubeDownloader-update")
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": f"YouTubeDownloader/{__version__}"}


class UpdateCancelled(Exception):
    pass


def is_installed_build() -> bool:
    # Solo el ejecutable empaquetado se puede actualizar con el instalador.
    return getattr(sys, "frozen", False)


def _parse_version(tag: str):
    try:
        return Version(tag.strip().lstrip("vV"))
    except InvalidVersion:
        return None


def check_for_update(timeout: int = 10):
    """Devuelve un dict con la release más nueva que tenga instalador, o None si ya es la última.

    Se usa la lista de releases y no /releases/latest porque las releases se publican como
    pre-release y /latest las ignora.
    """
    response = requests.get(RELEASES_API, params={"per_page": 30}, headers=HEADERS, timeout=timeout)
    response.raise_for_status()

    best = None
    for release in response.json():
        if release.get("draft"):
            continue
        version = _parse_version(release.get("tag_name", ""))
        asset = next((a for a in release.get("assets", []) if INSTALLER_RE.search(a.get("name", ""))), None)
        if version is None or asset is None:
            continue
        if best is None or version > best["version"]:
            digest = asset.get("digest") or ""
            best = {
                "version": version,
                "tag": release["tag_name"],
                "notes": (release.get("body") or "").replace("\r\n", "\n").strip(),
                "url": release.get("html_url", REPO_URL),
                "asset_name": asset["name"],
                "asset_url": asset["browser_download_url"],
                "size": asset.get("size", 0),
                "sha256": digest.split(":", 1)[1] if digest.startswith("sha256:") else None,
            }

    if best and best["version"] > Version(__version__):
        return best
    return None


def download_installer(update: dict, progress_callback=None, is_cancelled=lambda: False) -> str:
    """Descarga el instalador a %TEMP% y comprueba tamaño y SHA-256. Devuelve la ruta."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    path = os.path.join(DOWNLOAD_DIR, os.path.basename(update["asset_name"]))
    partial = path + ".part"
    sha = hashlib.sha256()
    done = 0

    with requests.get(update["asset_url"], headers={"User-Agent": HEADERS["User-Agent"]},
                      stream=True, timeout=30) as response:
        response.raise_for_status()
        total = update["size"] or int(response.headers.get("Content-Length", 0))
        with open(partial, "wb") as f:
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if is_cancelled():
                    break
                f.write(chunk)
                sha.update(chunk)
                done += len(chunk)
                if progress_callback and total:
                    progress_callback(done / total)

    if is_cancelled():
        os.remove(partial)
        raise UpdateCancelled()
    if update["size"] and done != update["size"]:
        os.remove(partial)
        raise IOError(f"Descarga incompleta ({done} de {update['size']} bytes).")
    if update["sha256"] and sha.hexdigest() != update["sha256"]:
        os.remove(partial)
        raise IOError("La huella SHA-256 del instalador no coincide con la publicada en GitHub.")

    os.replace(partial, path)
    return path


def launch_installer(path: str):
    """Lanza el instalador (pide permisos de administrador). /update=1 hace que vuelva a abrir la app."""
    args = "/SILENT /NORESTART /CLOSEAPPLICATIONS /update=1"
    # Si se instaló solo para este usuario (en %LOCALAPPDATA%), se actualiza igual y sin pedir administrador.
    local = os.path.normcase(os.environ.get("LOCALAPPDATA", ""))
    if local and os.path.normcase(sys.executable).startswith(local):
        args += " /CURRENTUSER"
    # os.startfile usa ShellExecute, que sí muestra el aviso de UAC; subprocess fallaría con el error 740.
    os.startfile(path, "open", args)


def cleanup_downloads():
    # Borra instaladores de actualizaciones anteriores (ya instaladas o abandonadas).
    try:
        for name in os.listdir(DOWNLOAD_DIR):
            os.remove(os.path.join(DOWNLOAD_DIR, name))
    except OSError:
        pass
