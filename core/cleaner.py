"""
WhatsClean Desktop - Safe Cleaner Engine
Native Windows Recycle Bin integration and secure file deletion / archiving.
"""

import ctypes
import os
import shutil
from ctypes import wintypes
from pathlib import Path
from typing import Any

FO_DELETE = 0x0003
FOF_ALLOWUNDO = 0x0040        # Move to Windows Recycle Bin
FOF_NOCONFIRMATION = 0x0010   # Silent, no prompt dialog
FOF_SILENT = 0x0004           # No progress bar UI
FOF_NOERRORUI = 0x0400        # Suppress Windows error dialogs


class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", wintypes.WORD),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", wintypes.LPVOID),
        ("lpszProgressTitle", wintypes.LPCWSTR),
    ]


def _recycle_batch(paths: list[str]) -> tuple[int, list[str]]:
    """
    Sends a list of files to the Windows Recycle Bin using SHFileOperationW.
    Returns (success_count, failed_paths).
    """
    if not paths:
        return 0, []

    valid_paths = [os.path.abspath(p) for p in paths if os.path.exists(p)]
    if not valid_paths:
        return 0, []

    # Windows API expects a null-separated, double-null-terminated string
    pfrom = "\0".join(valid_paths) + "\0\0"

    fileop = SHFILEOPSTRUCTW()
    fileop.hwnd = None
    fileop.wFunc = FO_DELETE
    fileop.pFrom = pfrom
    fileop.pTo = None
    fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI

    ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))

    # Verify which files were actually deleted

    succeeded = 0
    failed = []
    for p in valid_paths:
        if not os.path.exists(p):
            succeeded += 1
        else:
            failed.append(p)

    return succeeded, failed


def delete_files(paths: list[str], to_recycle_bin: bool = True, batch_size: int = 100) -> dict[str, Any]:
    """
    Safely deletes a list of files.
    Defaults to Windows Recycle Bin.
    """
    total_requested = len(paths)
    bytes_freed = 0
    succeeded = 0
    failed = []

    # Calculate sizes before deletion
    size_map = {}
    for p in paths:
        try:
            if os.path.exists(p):
                size_map[p] = os.path.getsize(p)
        except (OSError, PermissionError):
            size_map[p] = 0

    if to_recycle_bin:
        for i in range(0, len(paths), batch_size):
            chunk = paths[i:i + batch_size]
            succ, fail = _recycle_batch(chunk)
            succeeded += succ
            failed.extend(fail)
            for p in chunk:
                if p not in fail and p in size_map:
                    bytes_freed += size_map[p]
    else:
        for p in paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
                    bytes_freed += size_map.get(p, 0)
                    succeeded += 1
            except (OSError, PermissionError) as err:
                failed.append(f"{p}: {err}")

    return {
        "requested": total_requested,
        "deleted": succeeded,
        "bytes_freed": bytes_freed,
        "failed_count": len(failed),
        "failed_items": failed[:20],
        "recycle_bin": to_recycle_bin,
    }


def archive_files(paths: list[str], destination_dir: str) -> dict[str, Any]:
    """
    Copies files to an external backup folder before clearing.
    """
    dest = Path(destination_dir)
    dest.mkdir(parents=True, exist_ok=True)

    archived = 0
    total_bytes = 0
    errors = []

    for p in paths:
        try:
            p_obj = Path(p)
            if p_obj.exists() and p_obj.is_file():
                target = dest / p_obj.name
                if target.exists():
                    target = dest / f"{p_obj.stem}_{os.urandom(3).hex()}{p_obj.suffix}"
                shutil.copy2(p, target)
                total_bytes += p_obj.stat().st_size
                archived += 1
        except (OSError, shutil.Error) as e:
            errors.append(f"{p}: {e!s}")

    return {
        "archived_count": archived,
        "total_bytes": total_bytes,
        "destination": str(dest.resolve()),
        "errors": errors[:20],
    }
