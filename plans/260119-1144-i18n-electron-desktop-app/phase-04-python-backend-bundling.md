# Phase 4: Python Backend Bundling

## Context Links
- [Plan Overview](plan.md)
- [Phase 3: Electron Setup](phase-03-electron-project-setup.md)
- [Electron Research](research/researcher-01-electron-python-integration.md)

## Overview
- **Priority**: P2
- **Status**: pending
- **Effort**: 3h
- **Description**: Bundle Python backend with PyInstaller for Windows .exe

## Key Insights
- PyInstaller `--onefile` creates single executable
- Need `.spec` file for complex hidden imports
- Gradio, deeppresenter, pptagent have many dependencies
- Playwright browsers need separate handling
- Output ~200-400MB expected

## Requirements

### Functional
- Single backend.exe that runs Gradio server
- All Python dependencies bundled
- Configuration files accessible
- Logs written to user cache directory

### Non-Functional
- Startup time <30s
- Executable size <500MB
- Works on Windows 10/11

## Architecture

```
python-dist/
└── backend.exe          # PyInstaller output

At runtime:
backend.exe
    ↓ spawns
Gradio server on localhost:7861
    ↓ serves
WebUI to Electron
```

## Related Code Files

### Create
- `D:/NCKH_2025/PPTAgent/backend.py` (wrapper for webui)
- `D:/NCKH_2025/PPTAgent/backend.spec` (PyInstaller config)
- `D:/NCKH_2025/PPTAgent/scripts/build-backend.ps1`

### Reference
- `D:/NCKH_2025/PPTAgent/webui.py`
- `D:/NCKH_2025/PPTAgent/deeppresenter/`
- `D:/NCKH_2025/PPTAgent/pptagent/`

## Implementation Steps

### Step 1: Create backend.py wrapper
```python
"""
Backend entry point for PyInstaller bundling.
Wraps webui.py with proper signal handling and logging.
"""
import sys
import signal
import logging
from pathlib import Path

# Setup logging before imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PPTAgent-Backend')

def signal_handler(sig, frame):
    logger.info('Shutdown signal received')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    logger.info('Starting PPTAgent backend...')

    # Import and run webui
    from webui import ChatDemo
    from deeppresenter.utils.constants import WORKSPACE_BASE

    chat_demo = ChatDemo()
    demo = chat_demo.create_interface()

    logger.info('Launching Gradio server on localhost:7861')
    demo.launch(
        debug=False,
        server_name='localhost',
        server_port=7861,
        share=False,
        max_threads=16,
        allowed_paths=[WORKSPACE_BASE],
    )

if __name__ == '__main__':
    main()
```

### Step 2: Create backend.spec
```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all data files and hidden imports
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
        ('deeppresenter/deeppresenter/config.yaml', 'deeppresenter/deeppresenter'),
        ('deeppresenter/deeppresenter/mcp.json', 'deeppresenter/deeppresenter'),
    ] + gradio_data,
    hiddenimports=[
        'gradio',
        'uvicorn',
        'starlette',
        'httpx',
        'websockets',
        'pydantic',
        'python-multipart',
        'aiofiles',
        'orjson',
        'platformdirs',
    ] + gradio_hiddenimports + deeppresenter_hiddenimports + pptagent_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'PIL.ImageTk',
    ],
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
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resource/pptagent-logo.ico',
)
```

### Step 3: Create build script (build-backend.ps1)
```powershell
# Build Python backend with PyInstaller
# Run from PPTAgent root directory

Write-Host "Building PPTAgent backend..."

# Ensure virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate and install
.\.venv\Scripts\Activate.ps1
pip install pyinstaller
pip install -e deeppresenter
pip install -r requirements.txt

# Clean previous builds
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue

# Build with spec file
Write-Host "Running PyInstaller..."
pyinstaller backend.spec --clean

# Copy to electron-app location
$destDir = "python-dist"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir
}
Copy-Item "dist/backend.exe" -Destination "$destDir/backend.exe" -Force

Write-Host "Build complete: python-dist/backend.exe"
```

### Step 4: Handle Playwright browsers
```python
# Add to backend.py before main()
import os

def setup_playwright():
    """Configure Playwright browser path for bundled app."""
    if getattr(sys, 'frozen', False):
        # Running as bundled exe
        bundle_dir = sys._MEIPASS
        browsers_path = os.path.join(bundle_dir, 'browsers')
        if os.path.exists(browsers_path):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
```

### Step 5: Test build locally
```bash
# From PPTAgent root
.\scripts\build-backend.ps1

# Test executable
.\python-dist\backend.exe
```

## Todo List
- [ ] Create backend.py wrapper script
- [ ] Create backend.spec with all hidden imports
- [ ] Create build-backend.ps1 script
- [ ] Add Playwright browser handling
- [ ] Convert pptagent-logo.png to .ico
- [ ] Test local build
- [ ] Verify all dependencies bundled
- [ ] Test backend.exe standalone
- [ ] Measure startup time and file size

## Success Criteria
- `backend.exe` builds without errors
- Executable starts Gradio server on :7861
- All API endpoints functional
- Size under 500MB

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing hidden imports | High | Test thoroughly, add to spec |
| Large file size | Medium | Use UPX compression |
| Slow startup | Medium | Acceptable for desktop app |
| Playwright browsers | High | Bundle or download on first run |

## Security Considerations
- Executable runs with user privileges
- No elevation required
- Config files in user directory

## Next Steps
→ Phase 5: Electron-Python IPC
