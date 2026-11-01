"""
WhatsClean Desktop - UI Bridge API
Exposes Python backend methods directly to the pywebview / HTML5 frontend.
"""

import os
import subprocess
from typing import Any

from core.cleaner import archive_files, delete_files
from core.scanner import get_last_findings_by_categories, run_full_scan


def format_bytes(num_bytes: int) -> str:
    """Formats bytes into human readable string (B, KB, MB, GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    elif num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"

class WhatsCleanAPI:
    """Bridge interface between JavaScript and Python backend."""

    def __init__(self):
        self._last_scan_data: dict[str, Any] | None = None

    def scan(self) -> dict[str, Any]:
        """Runs storage scan and returns structured stats."""
        data = run_full_scan()
        self._last_scan_data = data

        # Add human-formatted strings
        formatted_categories = {}
        for k, cat in data['categories'].items():
            cat_copy = dict(cat)
            cat_copy['size_formatted'] = format_bytes(cat['size_bytes'])
            # Format individual file preview items
            preview_files = []
            for f in cat['files']:
                preview_files.append({
                    'name': f['name'],
                    'path': f['path'],
                    'size': f['size'],
                    'size_formatted': format_bytes(f['size']),
                    'app': f.get('app', 'WhatsApp Desktop')
                })
            cat_copy['files'] = preview_files
            formatted_categories[k] = cat_copy

        apps_formatted = {}
        for app_name, app_stat in data['apps'].items():
            apps_formatted[app_name] = {
                'files_count': app_stat['files_count'],
                'total_bytes': app_stat['total_bytes'],
                'total_formatted': format_bytes(app_stat['total_bytes'])
            }

        return {
            'success': True,
            'apps': apps_formatted,
            'total_files': data['total_files'],
            'total_bytes': data['total_bytes'],
            'total_formatted': format_bytes(data['total_bytes']),
            'safe_bytes': data['safe_bytes'],
            'safe_formatted': format_bytes(data['safe_bytes']),
            'categories': formatted_categories
        }

    def clean(self, category_keys: list[str], to_recycle_bin: bool = True) -> dict[str, Any]:
        """Cleans selected categories and returns deletion report."""
        if not category_keys:
            return {'success': False, 'message': 'No categories selected'}

        paths = get_last_findings_by_categories(category_keys)
        if not paths:
            return {'success': False, 'message': 'No files found to clean in selected categories'}

        result = delete_files(paths, to_recycle_bin=to_recycle_bin)
        result['bytes_freed_formatted'] = format_bytes(result['bytes_freed'])
        result['success'] = True

        # Re-run scan to refresh state
        refreshed = self.scan()
        result['refreshed_scan'] = refreshed
        return result

    def open_in_explorer(self, file_path: str) -> dict[str, Any]:
        """Opens Windows Explorer and highlights the specific file."""
        if not file_path or not os.path.exists(file_path):
            return {'success': False, 'message': 'File not found on disk'}
        try:
            norm_path = os.path.normpath(file_path)
            subprocess.run(['explorer', f'/select,{norm_path}'], check=False)
            return {'success': True}
        except (OSError, subprocess.SubprocessError) as e:
            return {'success': False, 'error': str(e)}


    def archive_selected(self, category_keys: list[str], dest_folder: str) -> dict[str, Any]:
        """Archives selected category files to a user-specified backup directory."""
        if not category_keys:
            return {'success': False, 'message': 'No categories selected'}
        paths = get_last_findings_by_categories(category_keys)
        if not paths:
            return {'success': False, 'message': 'No files found to archive'}

        res = archive_files(paths, dest_folder)
        res['total_bytes_formatted'] = format_bytes(res['total_bytes'])
        res['success'] = True
        return res
