"""
WhatsClean Desktop - Local Standalone Executable Builder
Uses PyInstaller to package WhatsClean Desktop into a single .exe on Windows.
"""

import subprocess
import sys
from pathlib import Path


def build():
    print("=" * 60)
    print("  WhatsClean Desktop - Standalone Windows Builder")
    print("=" * 60)

    project_root = Path(__file__).resolve().parent
    main_script = project_root / "main.py"
    web_file = project_root / "ui" / "web" / "index.html"

    if not web_file.exists():
        print(f"[!] Error: Web UI asset not found at {web_file}")
        sys.exit(1)

    # PyInstaller add-data syntax on Windows uses semicolon separator
    data_arg = f"{web_file.resolve()};ui/web"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--noconsole",
        "--name=WhatsClean",
        f"--add-data={data_arg}",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--collect-all=webview",
        str(main_script.resolve()),
    ]

    print("[*] Starting PyInstaller compilation...")
    print(f"[*] Command: {' '.join(cmd)}\n")

    code = subprocess.call(cmd, cwd=str(project_root))

    if code == 0:
        exe_path = project_root / "dist" / "WhatsClean.exe"
        print("\n" + "=" * 60)
        print("  [SUCCESS] Build completed successfully!")
        print(f"  Executable created at: {exe_path}")
        print("=" * 60)
    else:
        print(f"\n[!] Compilation failed with return code: {code}")
        sys.exit(code)


if __name__ == "__main__":
    build()
