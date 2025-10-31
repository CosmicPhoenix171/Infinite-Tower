# Infinite Tower Engine - Web & Desktop Build Guide

## Overview
This project supports **two build targets**:
1. **Web (GitHub Pages)** - For demos and browser play using Pygbag
2. **Windows Desktop (Steam)** - Packaged as .exe using PyInstaller

## Web Build (GitHub Pages Demo)

### Prerequisites
```bash
pip install pygbag
```

### Project Structure for Web
The web build uses Pygbag to convert Pygame to WebAssembly that runs in browsers.

### Building for Web

1. **Create web-ready main file** (`main.py` in root):
   - Must use `asyncio` for browser compatibility
   - Entry point for Pygbag

2. **Build command**:
   ```bash
   pygbag --build infinite-tower-engine
   ```

3. **Test locally**:
   ```bash
   pygbag --build infinite-tower-engine
   # Opens browser at http://localhost:8000
   ```

4. **Deploy to GitHub Pages**:
   - Push to repository
   - Enable GitHub Pages in repo settings
   - Point to `/docs` or root with `index.html`

### Web Compatibility Notes
- Pygbag converts Pygame to run in browser via Emscripten
- Must use `async/await` pattern in main loop
- Some pygame features limited (no pygame.mixer in some browsers)
- Asset loading uses different paths

## Desktop Build (Steam/Windows)

### Prerequisites
```bash
pip install pyinstaller
```

### Building Windows Executable

1. **Build command**:
   ```bash
   pyinstaller --name="InfiniteTower" ^
               --onefile ^
               --windowed ^
               --icon=assets/icon.ico ^
               --add-data "assets;assets" ^
               demo_16bit_ui.py
   ```

2. **Output location**:
   - Executable: `dist/InfiniteTower.exe`
   - Standalone, no Python required

### Steam Integration (Future)
Once you're ready for Steam:
1. Initialize Steamworks SDK
2. Add achievements/cloud saves
3. Package with Steam installer
4. Upload to Steam Partner portal

## Dual-Target Architecture

### Recommended Structure
```
infinite-tower-engine/
├── src/                    # Core game code (shared)
│   └── infinite_tower/
├── demo_16bit_ui.py       # Desktop demo
├── main.py                # Web demo (async version)
├── build_web.py           # Web build script
├── build_desktop.py       # Desktop build script
├── requirements.txt       # Desktop dependencies
├── requirements-web.txt   # Web dependencies
└── docs/                  # GitHub Pages output
    └── index.html
```

## Current Status
- ✅ Core game engine working
- ✅ 16-bit UI system complete
- 🔄 Web version setup (in progress)
- ⏳ Desktop packaging (ready to implement)

## Next Steps
1. Create async web version of demo
2. Test with Pygbag locally
3. Deploy to GitHub Pages
4. Create PyInstaller spec for desktop build
