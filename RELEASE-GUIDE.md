# 🚀 Release Guide - How to Create a New Release

This guide explains how to use the automated GitHub Actions workflow to create releases.

## 📋 Overview

The release process is **fully automated** using GitHub Actions. You just need to:
1. Create and push a version tag
2. GitHub Actions automatically builds the `.exe` and creates the release
3. That's it! 🎉

## 🎯 Quick Start - Creating a Release

### Step 1: Prepare Your Code

Make sure all your changes are committed and pushed to the `main` branch:

```bash
git add .
git commit -m "Prepare for v1.0.0 release"
git push origin main
```

### Step 2: Create a Version Tag

Create a tag with the version number (must start with `v`):

```bash
# For version 1.0.0
git tag v1.0.0

# Push the tag to GitHub
git push origin v1.0.0
```

**That's it!** GitHub Actions will automatically:
- ✅ Build the Windows executable
- ✅ Create a GitHub Release
- ✅ Upload the `.exe` file
- ✅ Generate release notes

### Step 3: Monitor the Build

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You'll see the "Build and Release" workflow running
4. Wait for it to complete (usually 2-3 minutes)

### Step 4: Edit Release Notes (Optional)

Once the workflow completes:

1. Go to the **Releases** section
2. Find your new release
3. Click **Edit release**
4. Update the "What's New" section with your changes:

```markdown
### ✨ What's New
- Added support for 1Password format
- Improved error handling
- Fixed issue with special characters in passwords
- Updated UI with modern design
```

5. Click **Update release**

## 📝 Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **v1.0.0** - Major release (breaking changes)
- **v1.1.0** - Minor release (new features, backwards compatible)
- **v1.0.1** - Patch release (bug fixes)

### Examples:

```bash
# First public release
git tag v1.0.0

# Added new password manager support
git tag v1.1.0

# Fixed a bug
git tag v1.0.1

# Major rewrite with breaking changes
git tag v2.0.0
```

## 🔍 What the Workflow Does

Here's what happens automatically when you push a tag:

### 1. **Trigger** (`on: push: tags`)
- Detects when you push a tag like `v1.0.0`
- Only runs for version tags (format: `v*.*.*`)

### 2. **Setup** (Checkout & Python)
- Checks out your code
- Installs Python 3.11
- Installs all dependencies (PyInstaller, tkinterdnd2, Pillow)

### 3. **Build** (PyInstaller)
- Runs PyInstaller to create the `.exe`
- Uses `--onefile` for single executable
- Uses `--windowed` for no console window
- Includes the icon
- Cleans previous builds

### 4. **Verify**
- Checks that the `.exe` was created
- Reports the file size
- Fails if build unsuccessful

### 5. **Create Release**
- Creates a new GitHub Release
- Uploads the `.exe` file
- Generates release notes template
- Makes it public immediately

### 6. **Artifacts**
- Keeps the `.exe` as a downloadable artifact for 7 days
- Useful for testing before making public

## 🛠️ Workflow File Explained

The workflow is defined in `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*.*.*'  # Only run on version tags
```

**When it runs:** Only when you push a tag matching `v*.*.*` pattern.

```yaml
runs-on: windows-latest
```

**Where it runs:** On a Windows machine (needed to build `.exe` files).

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
```

**What it does:** Downloads your repository code.

```yaml
  - name: Install dependencies
    run: |
      pip install pyinstaller tkinterdnd2 Pillow
```

**What it does:** Installs Python packages needed to build.

```yaml
  - name: Build executable
    run: |
      pyinstaller --name="TrueKey-Migration-Tool" ...
```

**What it does:** Creates the Windows `.exe` file using PyInstaller.

```yaml
  - name: Create Release
    uses: softprops/action-gh-release@v1
```

**What it does:** Creates the GitHub Release and uploads files.

## 🔧 Customizing the Workflow

### Change the Python Version

Edit this line:
```yaml
python-version: '3.11'  # Change to '3.10', '3.12', etc.
```

### Add More Build Platforms

To build for Mac/Linux, add more jobs:

```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    # ... existing steps
  
  build-macos:
    runs-on: macos-latest
    # ... similar steps with different PyInstaller commands
```

### Change Release Notes Template

Edit the `body:` section in the workflow:

```yaml
body: |
  ## Your custom release notes here
  
  ### Features
  - Feature 1
  - Feature 2
```

## 🐛 Troubleshooting

### Problem: Workflow doesn't run

**Check:**
- Did you push the tag? (`git push origin v1.0.0`)
- Is the tag format correct? (must be `v*.*.*`)
- Go to Actions tab - any error messages?

### Problem: Build fails

**Check the Actions log:**
1. Go to Actions tab
2. Click on the failed workflow run
3. Click on "build-windows" job
4. Expand the failed step to see error details

**Common issues:**
- Missing dependency: Add to `pip install` command
- Import error: Check all imports in your code
- Icon not found: Make sure `icon.ico` exists in repository

### Problem: Release created but no .exe file

**Check:**
1. Look at the "Build executable" step in Actions log
2. Check if build completed successfully
3. Verify `dist/TrueKey-Migration-Tool.exe` was created

### Problem: Need to delete a release

```bash
# Delete the release on GitHub (via web interface)
# Then delete the tag locally and remotely:
git tag -d v1.0.0                    # Delete local tag
git push origin --delete v1.0.0      # Delete remote tag
```

## 📊 Viewing Build Status

Add a badge to your README.md:

```markdown
![Build Status](https://github.com/yourusername/truekey-migration-tool/workflows/Build%20and%20Release/badge.svg)
```

## ✅ Pre-Release Checklist

Before creating a release, make sure:

- [ ] All code is committed and pushed
- [ ] Version number is decided (following semver)
- [ ] CHANGELOG or release notes are prepared
- [ ] Icon file (`icon.ico`) is in the repository
- [ ] Code is tested and working
- [ ] README is up to date

## 🎓 Example: First Release

Here's a complete example of creating your first release:

```bash
# 1. Make sure everything is ready
git status
git pull origin main

# 2. Commit any final changes
git add .
git commit -m "Ready for v1.0.0 release"
git push origin main

# 3. Create and push the tag
git tag v1.0.0
git push origin v1.0.0

# 4. Watch it build on GitHub
# Go to: https://github.com/yourusername/your-repo/actions

# 5. After 2-3 minutes, check your release
# Go to: https://github.com/yourusername/your-repo/releases

# 6. Download and test the .exe file

# 7. Edit the release notes if needed
```

## 🔄 Creating Subsequent Releases

For future releases:

```bash
# Make your changes
git add .
git commit -m "Add new features"
git push origin main

# Create new version tag
git tag v1.1.0
git push origin v1.1.0

# Done! The workflow handles the rest
```

## 📞 Getting Help

If you run into issues:

1. Check the [Actions log](../../actions) for detailed error messages
2. Review this guide for common problems
3. Check [GitHub Actions documentation](https://docs.github.com/en/actions)
4. Open an issue if you need help

## 🎉 Success!

Once your workflow completes successfully, you'll have:

- ✅ A new release in the Releases section
- ✅ A downloadable `.exe` file
- ✅ Automatic release notes
- ✅ Users can download and use your app immediately!

Your repository is now fully automated for releases! 🚀
