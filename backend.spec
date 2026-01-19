# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

gradio_data, gradio_binaries, gradio_hiddenimports = collect_all('gradio')
deeppresenter_hiddenimports = collect_submodules('deeppresenter')
pptagent_hiddenimports = collect_submodules('pptagent')

a = Analysis(
    ['backend.py'],
    pathex=[],
    binaries=gradio_binaries,
    datas=[
        ('locales', 'locales'),
        ('pptagent/templates', 'pptagent/templates'),
    ] + gradio_data,
    hiddenimports=[
        'gradio', 'uvicorn', 'starlette', 'httpx', 'websockets',
        'pydantic', 'python-multipart', 'aiofiles', 'orjson', 'platformdirs',
    ] + gradio_hiddenimports + deeppresenter_hiddenimports + pptagent_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'PIL.ImageTk'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
