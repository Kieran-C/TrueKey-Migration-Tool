# Building the Executable

This guide explains how to build the standalone Windows executable for distribution.

## Prerequisites

1. **Python 3.7+** installed
2. **PyInstaller** for creating executables

```bash
pip install pyinstaller
```

3. **Optional dependencies** (recommended for full features):
```bash
pip install tkinterdnd2 Pillow
```

## Building the Executable

### Option 1: Quick Build (Recommended)

Run PyInstaller with the following command:

```bash
pyinstaller --name="TrueKey-Migration-Tool" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --hidden-import=gui ^
    --hidden-import=gui.app ^
    --hidden-import=gui.widgets ^
    --hidden-import=gui.styles ^
    main.py
```

**Command breakdown:**
- `--name` - Sets the executable name
- `--onefile` - Creates a single .exe file (easier to distribute)
- `--windowed` - No console window (clean UI-only app)
- `--icon` - Sets the application icon
- `--add-data` - Includes the icon file in the bundle
- `--hidden-import` - Explicitly includes the gui module and submodules
- `main.py` - Entry point

### Option 2: Using a Spec File

Create a file named `build.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[
        'gui',
        'gui.app',
        'gui.widgets',
        'gui.styles',
        'tkinterdnd2',
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
    name='TrueKey-Migration-Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
```

Then build with:

```bash
pyinstaller build.spec
```

## Output

The executable will be created in the `dist/` folder:
- `dist/TrueKey-Migration-Tool.exe` - Your distributable file

## Testing the Executable

1. Navigate to `dist/`
2. Run `TrueKey-Migration-Tool.exe`
3. Test all features:
   - Drag & drop file input
   - Browse for files
   - All three conversion formats
   - Notes export
   - Custom vault names

## Troubleshooting

### "Failed to execute script" error

**Cause**: Missing dependencies

**Solution**: Make sure all imports are included. Add to `hiddenimports` in spec file:
```python
hiddenimports=['gui', 'gui.app', 'gui.widgets', 'gui.styles', 'tkinterdnd2', 'PIL'],
```

### Large file size

**Cause**: PyInstaller includes entire Python environment

**Solutions**:
1. Use UPX compression (already enabled with `upx=True`)
2. Exclude unused modules:
```python
excludes=['numpy', 'pandas', 'matplotlib'],
```

### Icon not showing

**Cause**: Icon file not included or wrong format

**Solution**: 
1. Ensure `icon.ico` exists and is multi-resolution
2. Check `datas` includes the icon
3. Verify icon path in `--icon` parameter

### DLL errors on other computers

**Cause**: Missing Visual C++ redistributables

**Solution**: Users need to install:
- [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

Or use `--onefile` mode (already default in our build).

## Optimizing File Size

Current build is ~15-25 MB. To reduce:

### 1. Exclude unnecessary modules
```bash
--exclude-module numpy ^
--exclude-module pandas ^
--exclude-module matplotlib
```

### 2. Use UPX compression
```bash
pip install upx-windows
pyinstaller ... --upx-dir="C:\path\to\upx"
```

### 3. Strip debug symbols
Already done with `strip=False` in spec file (paradoxically, False is faster)

## Code Signing (Optional)

For production releases, consider code signing to avoid Windows SmartScreen warnings:

1. Obtain a code signing certificate
2. Use `signtool.exe`:
```bash
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 TrueKey-Migration-Tool.exe
```

Without signing, users will see "Unknown publisher" warning but can still run the app.

## GitHub Release Checklist

Before uploading to GitHub:

- [ ] Test the executable on a clean Windows machine
- [ ] Verify all features work
- [ ] Check file size is reasonable (<30 MB)
- [ ] Ensure icon displays correctly
- [ ] Test with sample TrueKey CSV files
- [ ] Create release notes
- [ ] Tag the release with version number (e.g., v1.0.0)

## Distribution

1. Upload `TrueKey-Migration-Tool.exe` to GitHub Releases
2. Include release notes with:
   - New features
   - Bug fixes
   - Known issues
3. Mark as "Latest release"
4. Update README download link

## Build Scripts

For convenience, create `build.bat`:

```batch
@echo off
echo Building TrueKey Migration Tool...

pyinstaller --name="TrueKey-Migration-Tool" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --hidden-import=gui ^
    --hidden-import=gui.app ^
    --hidden-import=gui.widgets ^
    --hidden-import=gui.styles ^
    --clean ^
    main.py

echo.
echo Build complete! Check dist/ folder.
pause
```

Run with: `build.bat`

## Version Management

Update version in release:

1. In `gui/app.py`, add version constant:
```python
VERSION = "1.0.0"
```

2. Display in window title:
```python
self.root.title(f"TrueKey Migration Tool v{VERSION}")
```

3. Tag GitHub release with same version
