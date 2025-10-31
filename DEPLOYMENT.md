# Infinite Tower - Deployment Guide

## 🎮 Two Build Targets

### 1. 🌐 Web Demo (GitHub Pages)
Play instantly in browser - perfect for testing and demos

### 2. 💻 Desktop (Windows EXE for Steam)
Full desktop experience for Steam distribution

---

## 🌐 Web Build (GitHub Pages)

### Quick Start
```bash
# Install web dependencies
pip install -r requirements-web.txt

# Build for web
python build_web.py

# Test locally
python -m pygbag infinite-tower-engine
# Opens at http://localhost:8000
```

### Deploy to GitHub Pages

1. **Build the project**:
   ```bash
   python build_web.py
   ```

2. **Create `docs` folder** (if not exists):
   ```bash
   mkdir docs
   ```

3. **Copy build output**:
   ```bash
   # After pygbag builds, copy the web files
   cp -r build/web/* docs/
   ```

4. **Push to GitHub**:
   ```bash
   git add docs/
   git commit -m "Deploy web demo"
   git push origin main
   ```

5. **Enable GitHub Pages**:
   - Go to repo Settings → Pages
   - Source: Deploy from branch
   - Branch: main
   - Folder: /docs
   - Save

6. **Access your game**:
   ```
   https://CosmicPhoenix171.github.io/Infinite-Tower/
   ```

### Web Features
- ✅ Runs in any modern browser
- ✅ No installation required
- ✅ Perfect for demos and testing
- ✅ Mobile-friendly (with touch controls)
- ⚠️ Some features limited (audio, file I/O)

---

## 💻 Desktop Build (Windows EXE)

### Quick Start
```bash
# Install desktop dependencies
pip install -r requirements-desktop.txt

# Build Windows executable
python build_desktop.py
```

### Output
- **Executable**: `infinite-tower-engine/dist/InfiniteTower.exe`
- **Release copy**: `infinite-tower-engine/release/InfiniteTower.exe`

### Testing
```bash
# Navigate to release folder
cd infinite-tower-engine/release

# Run the executable
./InfiniteTower.exe
```

### Desktop Features
- ✅ Standalone executable (no Python needed)
- ✅ Full performance (no browser overhead)
- ✅ Complete audio/graphics support
- ✅ File system access
- ✅ Steam ready

---

## 🚀 Steam Preparation

Once you're ready for Steam release:

### 1. Get Steam Partner Account
- Sign up at https://partner.steamgames.com/
- Pay $100 USD app fee

### 2. Integrate Steamworks SDK
```bash
# Install steamworks
pip install steamworks

# Add to your code:
from steamworks import STEAMWORKS
STEAMWORKS.initialize()
```

### 3. Add Steam Features
- Achievements
- Cloud saves
- Leaderboards
- Workshop support
- Steam Overlay

### 4. Create Steam Build
```bash
# Use SteamCMD to upload
steamcmd +login username +run_app_build ../scripts/app_build.vdf +quit
```

### 5. Set Pricing & Release
- Set store page details
- Upload screenshots/videos
- Set pricing
- Submit for review
- Launch!

---

## 📁 Project Structure

```
Infinite-Tower/
├── infinite-tower-engine/
│   ├── main.py              # 🌐 Web entry point (async)
│   ├── demo_16bit_ui.py     # 💻 Desktop demo
│   ├── src/                 # Shared game code
│   ├── assets/              # Game assets
│   ├── dist/                # Built executables
│   └── release/             # Release-ready files
├── docs/                    # 🌐 GitHub Pages output
├── build_web.py             # 🌐 Web build script
├── build_desktop.py         # 💻 Desktop build script
├── requirements-web.txt     # 🌐 Web dependencies
├── requirements-desktop.txt # 💻 Desktop dependencies
└── BUILD_GUIDE.md          # This file
```

---

## 🔧 Development Workflow

### Local Testing
```bash
# Test desktop version
cd infinite-tower-engine
python demo_16bit_ui.py

# Test web version
python -m pygbag infinite-tower-engine
```

### Building Releases

**For GitHub Pages demo**:
```bash
python build_web.py
# Copy build/web/* to docs/
# Commit and push
```

**For Steam/Windows**:
```bash
python build_desktop.py
# Test infinite-tower-engine/release/InfiniteTower.exe
# Package for Steam when ready
```

---

## 🎯 Recommended Workflow

1. **Develop** using desktop demo (`demo_16bit_ui.py`)
2. **Test** web version with Pygbag (`main.py`)
3. **Deploy** demo to GitHub Pages for feedback
4. **Polish** based on feedback
5. **Build** final Windows .exe
6. **Package** for Steam
7. **Release** on Steam!

---

## 📋 Current Status

- ✅ Core game engine complete
- ✅ 16-bit UI system done
- ✅ Web build setup ready
- ✅ Desktop build scripts ready
- ⏳ GitHub Pages deployment (ready to deploy)
- ⏳ Steam integration (when ready)

---

## 🆘 Troubleshooting

### Web build fails
- Make sure pygbag is installed: `pip install pygbag`
- Check that `main.py` uses `async/await`
- Verify all imports work with web paths

### Desktop build fails
- Install PyInstaller: `pip install pyinstaller`
- Check all dependencies are in requirements-desktop.txt
- Make sure asset paths are correct

### GitHub Pages not showing
- Check that Pages is enabled in Settings
- Verify docs/ folder contains index.html
- Wait a few minutes for deployment
- Check GitHub Actions for build errors

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/CosmicPhoenix171/Infinite-Tower/issues
- Steam Partner: https://partner.steamgames.com/support

---

**Good luck with your launch! 🚀**
