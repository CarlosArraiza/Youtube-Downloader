# -*- mode: python ; coding: utf-8 -*-

import re

block_cipher = None

# La versión sale de src/version.py; version.txt (recursos del .exe) se genera aquí.
with open('src/version.py', encoding='utf-8') as f:
    APP_VERSION = re.search(r'__version__\s*=\s*"([^"]+)"', f.read()).group(1)
_v = tuple(int(x) for x in (APP_VERSION.split('.') + ['0', '0', '0'])[:4])
with open('version.txt', 'w', encoding='utf-8') as f:
    f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={_v}, prodvers={_v}, mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable(u'040904B0', [
      StringStruct(u'CompanyName', u''),
      StringStruct(u'FileDescription', u'YouTube Downloader'),
      StringStruct(u'FileVersion', u'{APP_VERSION}'),
      StringStruct(u'InternalName', u'YouTubeDownloader'),
      StringStruct(u'ProductName', u'YouTube Downloader'),
      StringStruct(u'ProductVersion', u'{APP_VERSION}')])]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
""")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('C:\\ffmpeg\\bin\\ffmpeg.exe', '.'),
        ('C:\\ffmpeg\\bin\\ffprobe.exe', '.'),
    ],
    datas=[
        ('src', 'src'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'customtkinter',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'darkdetect',
        'packaging',
        'mutagen',
        'brotli',
        'pycryptodomex',
        'websockets',
        'certifi',
        'requests',
        'urllib3',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFilter',
        'PIL.ImageOps',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTubeDownloader',   # nombre fijo: el instalador actualiza en el sitio y no deja .exe viejos
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
    icon='assets/icon.ico',
)

COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTubeDownloader',
)
