"""
WhatsClean Desktop - Desktop App Runner
Launches the native desktop window using pywebview with Edge WebView2.
"""

import sys
from pathlib import Path

import webview

from ui.api import WhatsCleanAPI


def get_web_asset_path() -> Path:
    """Resolves index.html path both in standard run and PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        bundle_path = Path(sys._MEIPASS) / 'ui' / 'web' / 'index.html'
        if bundle_path.exists():
            return bundle_path
    return Path(__file__).parent / 'web' / 'index.html'


def start_app():
    """Initializes and runs the WhatsClean Desktop application."""
    api = WhatsCleanAPI()
    index_html = get_web_asset_path()

    webview.create_window(
        title='WhatsClean Desktop - Private Storage Cleaner',
        url=str(index_html.resolve()),

        js_api=api,
        width=1040,
        height=740,
        min_size=(820, 580),
        background_color='#090d16',
    )

    webview.start(debug=False)
