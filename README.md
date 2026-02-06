# TrueKey Migration Tool

Easily convert your TrueKey password exports to **Proton Pass**, **LastPass**, or **1Password** formats.

![TrueKey Migration Tool](https://img.shields.io/badge/Windows-Compatible-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🔄 **Convert to Multiple Password Managers**
  - Proton Pass
  - LastPass  
  - 1Password

- 📝 **Export Everything**
  - All your passwords and logins
  - Secure notes (optional)
  - Custom vault organization (Proton Pass)

- 🎨 **Easy to Use**
  - Simple drag & drop interface
  - Clear instructions and helpful tips
  - Modern, clean design

---

## 📥 Download & Installation

### For Windows Users (Easy Way)

1. Go to the [**Releases**](../../releases) page
2. Download the latest `TrueKey-Migration-Tool.exe` file
3. Double-click to run - **no installation needed!**

> **Note:** Windows may show a security warning because the app isn't code-signed. Click "More info" then "Run anyway" to proceed.

### For Python Users (Advanced)

<details>
<summary>Click to expand Python installation instructions</summary>

**Requirements:**
- Python 3.7 or higher

**Setup:**
```bash
# Clone the repository
git clone https://github.com/yourusername/truekey-migration-tool.git
cd truekey-migration-tool

# Run the application
python main.py
```

**Optional enhancements:**
```bash
pip install tkinterdnd2  # For drag & drop support
pip install Pillow       # For custom icon support
```

</details>

---

## 🚀 How to Use

### Step 1: Export from TrueKey

1. Open **TrueKey**
2. Go to **Settings** → **App Settings** → **Export Data**
3. Click **Continue** and enter your master password
4. **Save** the CSV file to your computer

> 💡 *Need help? Hover over the question mark (?) icon in the app for detailed instructions*

### Step 2: Convert Your Data

1. **Launch** the TrueKey Migration Tool
2. **Choose** your destination password manager from the dropdown
3. **Drag & drop** your TrueKey CSV file (or click to browse)
4. **Select** where to save your converted file
5. *(Optional)* Check "Export notes to separate file" if you want notes exported
6. *(Optional)* For Proton Pass, you can customize the vault name
7. Click **Convert** and wait for completion!

### Step 3: Import to Your Password Manager

**Proton Pass:**
- Open Proton Pass → Settings → Import → Upload your converted CSV

**LastPass:**
- Open LastPass → More Options → Advanced → Import → Upload your file

**1Password:**
- Open 1Password → File → Import → Select the converted CSV

---

## ❓ Frequently Asked Questions

**Q: Is this safe? Will my passwords be exposed?**  
A: Yes, it's safe! The conversion happens entirely on your computer - nothing is uploaded to the internet. Your data never leaves your device.

**Q: What if I get an error?**  
A: Make sure you're using the CSV file exported directly from TrueKey. If problems persist, check that the file isn't corrupted and try exporting from TrueKey again.

**Q: Can I convert multiple times?**  
A: Absolutely! Feel free to test the conversion with different password managers before making your final choice.

**Q: Will this work on Mac/Linux?**  
A: The Windows .exe is Windows-only. Mac/Linux users can run the Python version (see Advanced installation above).

---

## 🛠️ For Developers

Interested in contributing or modifying the tool?

**Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Code structure and design patterns
- [BUILDING.md](BUILDING.md) - How to build the executable manually
- [RELEASE-GUIDE.md](RELEASE-GUIDE.md) - How to create releases with GitHub Actions

**Quick overview:**
- `converter.py` - CSV conversion logic
- `gui/app.py` - Main application window
- `gui/widgets.py` - Custom UI components
- `gui/styles.py` - Colors and theme

**Creating a Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions automatically builds and releases!
```

---

## 📝 License

MIT License - Free to use and modify for personal or commercial purposes.

---

## 💬 Support & Feedback

- 🐛 **Found a bug?** Open an [issue](../../issues)
- 💡 **Have a suggestion?** Open an [issue](../../issues) with your idea
- ⭐ **Like the tool?** Give it a star on GitHub!

---

## 🙏 Acknowledgments

Created to help users migrate from Intel TrueKey to modern password managers.

**Special thanks to:**
- The open-source community
