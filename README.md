# WhatsClean Desktop

> **A fast, privacy-first, zero-telemetry desktop utility to reclaim gigabytes of hidden caches from WhatsApp Desktop on Windows.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://microsoft.com)
[![Zero Telemetry](https://img.shields.io/badge/Telemetry-Zero%20%2F%20100%25%20Offline-10b981.svg)](#privacy-guarantee)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

---

## The Problem
On Windows 10 and 11, the official WhatsApp Desktop (UWP/MSIX package) stores temporary WebViews, rotated debug logs, network buffers, and downloaded media caches silently in `%LocalAppData%\Packages\`.

Over time, this hidden cache grows from **5 GB to over 30 GB**, turning your Windows `C:` drive red without appearing in standard Add/Remove Programs.

## Features
- **1-Click Safe Clean**: Reclaim gigabytes of application web cache and debug traces without losing chats or contact history.
- **Windows Recycle Bin Safety**: Deleted items are sent to the native Windows Recycle Bin by default — you can undo or restore any item anytime.
- **Categorized Breakdown**:
  - `Application Web Cache` (WebView2, service workers, network buffers)
  - `Diagnostic & Crash Logs` (rotated logs, crash telemetry)
  - `Temporary Media & Downloads` (ephemeral download stages)
  - `Cached Stickers & WebP`
  - `Voice Notes & Audio` (flagged with cautionary review)
  - `Forwarded Media & Large Videos`
- **File Inspector**: Preview files with exact size and click *Show in Folder* to view in Windows Explorer.
- **Zero Telemetry & 100% Offline**: No network requests, no analytics, no external servers.
- **CLI Mode**: Run headlessly in Windows Task Scheduler for automatic scheduled background cleanup.
- **Ultra-Lightweight**: Built with native Edge WebView2 (`pywebview`). Consumes < 40MB RAM compared to 500MB+ bloated Electron apps.

---

## Quick Start

### 1. Prerequisites
- Windows 10 or 11
- Python 3.10 or newer

### 2. Clone and Run
```bash
# Clone the repository
git clone https://github.com/jamamjadalone/whatsclean-desktop.git
cd whatsclean-desktop

# Install lightweight dependencies
pip install -r requirements.txt

# Launch Desktop App
python main.py
```

---

## Local Standalone Executable Build

You can bundle WhatsClean Desktop into a single standalone `.exe` locally without any cloud dependencies:

```bash
# Install PyInstaller
pip install pyinstaller

# Run the automated build script
python build_exe.py
```

The resulting executable will be created at `dist/WhatsClean.exe` — ready to run on any Windows 10/11 PC without needing Python installed!

---

## CLI Automation (Power Users & Scheduled Tasks)

Run storage scans and cleanups directly from PowerShell or Command Prompt:

```bash
# View storage consumption in terminal
python main.py --scan

# Preview what would be cleaned without touching disk
python main.py --dry-run --clean-safe

# Clean all safe junk caches to Windows Recycle Bin
python main.py --clean-safe
```

### Windows Task Scheduler (Weekly Auto-Clean)
To automatically clean your cache every Sunday at midnight without opening the GUI:
```powershell
schtasks /create /tn "WhatsCleanAutoWeekly" /tr "python C:\path\to\WhatsClean\main.py --clean-safe" /sc weekly /d SUN /st 00:00
```

---

## Architecture and How It Works

WhatsClean Desktop inspects local WhatsApp application sandboxes directly:
- **WhatsApp Desktop (UWP/MSIX)**: `%LocalAppData%\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\`
- **WhatsApp Classic (AppData)**: `%AppData%\WhatsApp\`

```
WhatsClean/
├── core/
│   ├── scanner.py      # Scans and classifies local WhatsApp sandboxes
│   └── cleaner.py      # Safe deletion via native Windows SHFileOperationW
├── ui/
│   ├── api.py          # Python-to-JavaScript bridge
│   ├── app.py          # Pywebview desktop window wrapper
│   └── web/
│       └── index.html  # Dark dev dashboard (Self-contained offline UI)
├── build_exe.py        # Local PyInstaller standalone executable builder
├── main.py             # Dual entry point (GUI + CLI)
└── requirements.txt
```

---

## Contributing
Contributions are warmly welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues, suggesting enhancements, or submitting PRs.

---

## Privacy Guarantee
- **Zero Network Traffic**: WhatsClean Desktop does not make any HTTP or network requests.
- **No Cloud Upload**: None of your files, logs, or chat data leave your computer.
- **Open Source**: Full codebase is inspectable in under 10 minutes.

---

## Legal Disclaimer
WhatsClean Desktop is an independent open-source utility created for storage maintenance on Windows. It is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by WhatsApp LLC or Meta Platforms, Inc. All product and company names are the registered trademarks of their original owners.

---

## License
This project is licensed under the [MIT License](LICENSE).
