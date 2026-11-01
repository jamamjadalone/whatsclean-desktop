import os
from pathlib import Path

CATEGORY_APP_CACHE = 'app_cache'
CATEGORY_MEDIA_TEMP = 'media_temp'
CATEGORY_VOICE_PTT = 'voice_ptt'
CATEGORY_STICKERS = 'stickers'
CATEGORY_LARGE_VIDEOS = 'large_videos'
CATEGORY_LOGS = 'logs'

MEDIA_EXTENSIONS = {
    CATEGORY_VOICE_PTT: {'.opus', '.ogg', '.m4a'},
    CATEGORY_STICKERS: {'.webp'},
    CATEGORY_LARGE_VIDEOS: {'.mp4', '.mkv', '.avi', '.mov'},
    CATEGORY_LOGS: {'.log', '.txt', '.etl'},
}

CATEGORY_META = {
    CATEGORY_APP_CACHE: {
        'title': 'Application Web Cache',
        'desc': 'Cached web views, service workers, and network buffers',
        'color': '#38bdf8',
        'safe_to_clean': True,
    },
    CATEGORY_LOGS: {
        'title': 'Diagnostic & Crash Logs',
        'desc': 'Rotated debug traces and telemetry reports',
        'color': '#94a3b8',
        'safe_to_clean': True,
    },
    CATEGORY_MEDIA_TEMP: {
        'title': 'Temporary Media Downloads',
        'desc': 'Incomplete downloads, ephemeral staging files',
        'color': '#f59e0b',
        'safe_to_clean': True,
    },
    CATEGORY_STICKERS: {
        'title': 'Cached Stickers & WebP',
        'desc': 'Downloaded group stickers and custom animated emoji',
        'color': '#c084fc',
        'safe_to_clean': True,
    },
    CATEGORY_VOICE_PTT: {
        'title': 'Voice Notes & Audio',
        'desc': 'Received audio notes (Opus / Ogg / M4A)',
        'color': '#10b981',
        'safe_to_clean': False,
    },
    CATEGORY_LARGE_VIDEOS: {
        'title': 'Forwarded Media & Videos',
        'desc': 'Large video clips and attachments (> 10MB)',
        'color': '#ef4444',
        'safe_to_clean': False,
    },
}

def get_whatsapp_uwp_root():
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if not local_app_data:
        return None
    pkg_dir = Path(local_app_data) / 'Packages'
    if not pkg_dir.exists():
        return None
    for item in pkg_dir.glob('*WhatsAppDesktop*'):
        if item.is_dir():
            return item
    return None

def get_whatsapp_classic_root():
    app_data = os.environ.get('APPDATA', '')
    if not app_data:
        return None
    classic_path = Path(app_data) / 'WhatsApp'
    return classic_path if classic_path.exists() else None


def classify_file(path_obj, size):

    ext = path_obj.suffix.lower()
    parts = [p.lower() for p in path_obj.parts]

    if 'ebwebview' in parts or 'cache' in parts or 'code cache' in parts:
        return CATEGORY_APP_CACHE
    if 'rotatedlogs' in parts or 'logq' in parts or ext in MEDIA_EXTENSIONS[CATEGORY_LOGS]:
        return CATEGORY_LOGS
    if 'temp' in parts or 'tempstate' in parts or 'tmp' in parts:
        return CATEGORY_MEDIA_TEMP
    if ext in MEDIA_EXTENSIONS[CATEGORY_STICKERS]:
        return CATEGORY_STICKERS
    if ext in MEDIA_EXTENSIONS[CATEGORY_VOICE_PTT]:
        return CATEGORY_VOICE_PTT
    if ext in MEDIA_EXTENSIONS[CATEGORY_LARGE_VIDEOS]:
        return CATEGORY_LARGE_VIDEOS

    return CATEGORY_APP_CACHE

def scan_target(target_path):
    findings = []
    if not target_path or not os.path.exists(target_path):
        return findings

    try:
        for root, _, files in os.walk(target_path):
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    size = stat.st_size
                    p_obj = Path(full_path)
                    cat = classify_file(p_obj, size)
                    findings.append({
                        'path': full_path,
                        'name': f,
                        'size': size,
                        'category': cat,
                        'mtime': stat.st_mtime,
                    })
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass

    return findings

def get_app_targets():
    targets = {}
    uwp = get_whatsapp_uwp_root()
    if uwp:
        targets['WhatsApp Desktop'] = [
            uwp / 'LocalCache' / 'EBWebView' / 'Default' / 'Cache',
            uwp / 'LocalCache' / 'EBWebView' / 'Default' / 'Code Cache',
            uwp / 'LocalCache' / 'EBWebView' / 'Default' / 'Network',
            uwp / 'LocalState' / 'rotatedLogs',
            uwp / 'LocalState' / 'tmp',
            uwp / 'LocalState' / 'logq',
            uwp / 'TempState',
        ]
    classic = get_whatsapp_classic_root()
    if classic:
        targets['WhatsApp Classic'] = [classic / 'Cache', classic / 'logs']
    return targets


_LAST_FINDINGS = []

def get_last_findings_by_categories(category_keys=None):
    """Returns file paths matching the selected categories from last scan."""
    if not category_keys:
        return [f['path'] for f in _LAST_FINDINGS]
    selected_set = set(category_keys)
    return [f['path'] for f in _LAST_FINDINGS if f.get('category') in selected_set]


def run_full_scan():
    global _LAST_FINDINGS
    targets = get_app_targets()
    all_findings = []
    app_summary = {}

    for app_name, dir_list in targets.items():
        app_total_size = 0
        app_total_files = 0
        for directory in dir_list:
            if os.path.exists(directory):
                found = scan_target(directory)
                for item in found:
                    item['app'] = app_name
                all_findings.extend(found)
                app_total_files += len(found)
                app_total_size += sum(i['size'] for i in found)

        app_summary[app_name] = {
            'files_count': app_total_files,
            'total_bytes': app_total_size,
        }

    _LAST_FINDINGS = all_findings

    categories = {}
    for cat_key, meta in CATEGORY_META.items():
        cat_files = [f for f in all_findings if f['category'] == cat_key]
        total_size = sum(f['size'] for f in cat_files)
        categories[cat_key] = {
            'key': cat_key,
            'title': meta['title'],
            'desc': meta['desc'],
            'color': meta['color'],
            'safe_to_clean': meta['safe_to_clean'],
            'count': len(cat_files),
            'size_bytes': total_size,
            'files': cat_files[:60],
        }

    total_bytes = sum(f['size'] for f in all_findings)
    safe_bytes = sum(c['size_bytes'] for c in categories.values() if c['safe_to_clean'])

    return {
        'apps': app_summary,
        'total_files': len(all_findings),
        'total_bytes': total_bytes,
        'safe_bytes': safe_bytes,
        'categories': categories,
    }

