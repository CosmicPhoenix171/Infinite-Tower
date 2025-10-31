# 🎮 Deploy Your Web Game - Quick Guide

## ✅ What's Ready
Your game is **built and ready** for GitHub Pages!

### Files Created:
- `docs/index.html` - Main web game page
- `docs/infinite-tower-engine.apk` - Game package (WebAssembly)
- `docs/favicon.png` - Icon
- `docs/README.md` - Documentation

## 🚀 Deploy to GitHub Pages (3 Steps)

### Step 1: Commit and Push
```bash
git add docs/
git add build_web.py requirements-web.txt DEPLOYMENT.md
git commit -m "Add web-playable version"
git push origin main
```

### Step 2: Enable GitHub Pages
1. Go to your repo: https://github.com/CosmicPhoenix171/Infinite-Tower
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
5. Click **Save**

### Step 3: Wait & Play!
- GitHub will build your site (takes 1-2 minutes)
- Your game will be live at:
  
  **https://cosmicphoenix171.github.io/Infinite-Tower/**

## 🎯 Test It Out

Once deployed, you can:
- ✅ Share the link with friends
- ✅ Play on any device with a browser
- ✅ Test on mobile (touch controls should work)
- ✅ Embed in other websites

## 🔄 Update the Web Version

Whenever you make changes:

```bash
# 1. Build new version
cd infinite-tower-engine
cd ..
python -m pygbag --build infinite-tower-engine

# 2. Copy to docs
Copy-Item -Path "infinite-tower-engine\build\web\*" -Destination "docs\" -Recurse -Force

# 3. Commit and push
git add docs/
git commit -m "Update web version"
git push origin main
```

GitHub Pages will automatically update (takes 1-2 minutes).

## 📱 Features

Your web version includes:
- ✅ Full 16-bit UI
- ✅ Player movement with sprint
- ✅ Combat system
- ✅ Enemy AI
- ✅ Loot system
- ✅ Inventory & Equipment
- ✅ Health/Mana/Stamina bars
- ✅ Mini-map
- ✅ Damage numbers & notifications

## 🆘 Troubleshooting

### "404 - Page Not Found"
- Make sure you enabled Pages in Settings
- Check that `/docs` folder is selected
- Wait a few minutes for deployment

### "Game won't load"
- Check browser console (F12) for errors
- Try a different browser (Chrome, Firefox)
- Clear cache and refresh (Ctrl+Shift+R)

### "Want to update the game"
- Re-run the build command
- Copy files to docs/
- Commit and push

## 🎉 You're Live!

Once GitHub Pages is enabled, your game will be playable at:

**https://cosmicphoenix171.github.io/Infinite-Tower/**

Share this link anywhere! 🚀

---

*Current Status: Web build COMPLETE and ready to deploy!*
