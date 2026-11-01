#!/usr/bin/env python3
"""
WhatsClean Desktop - Privacy-First Windows Storage Cleaner
Entry point for GUI and CLI automation.
"""

import argparse

from ui.api import WhatsCleanAPI


def run_cli_scan():
    print("=" * 60)
    print("  WhatsClean Desktop - Storage Scan Report")
    print("=" * 60)
    api = WhatsCleanAPI()
    data = api.scan()

    print(f"Total Cached Storage: {data['total_formatted']} ({data['total_files']} files)")
    print(f"Safe to Clean:        {data['safe_formatted']}\n")

    print("Detected Applications:")
    for app, stats in data['apps'].items():
        print(f"  - {app}: {stats['total_formatted']} ({stats['files_count']} files)")

    print("\nStorage Breakdown by Category:")
    for cat in data['categories'].values():
        safety = "[SAFE]" if cat['safe_to_clean'] else "[CAUTION]"
        print(f"  {safety:<10} {cat['title']:<30} {cat['size_formatted']:>10} ({cat['count']} files)")
    print("=" * 60)



def run_cli_clean(dry_run: bool = False):
    api = WhatsCleanAPI()
    data = api.scan()
    safe_keys = [k for k, v in data['categories'].items() if v['safe_to_clean'] and v['count'] > 0]

    if not safe_keys:
        print("No safe cache files found to clean.")
        return

    print(f"Found safe categories to clean: {', '.join(safe_keys)}")
    print(f"Estimated space to reclaim: {data['safe_formatted']}")

    if dry_run:
        print("[DRY RUN] No files were deleted.")
        return

    res = api.clean(safe_keys, to_recycle_bin=True)
    if res.get('success'):
        print(f"Successfully cleaned {res['deleted']} files!")
        print(f"Reclaimed {res['bytes_freed_formatted']} (Moved to Windows Recycle Bin).")
    else:
        print(f"Cleaning error: {res.get('message')}")


def main():
    parser = argparse.ArgumentParser(
        description="WhatsClean Desktop - Privacy-first Windows storage cleaner for WhatsApp Desktop caches."
    )

    parser.add_argument("--scan", action="store_true", help="Perform scan and display findings in terminal")
    parser.add_argument("--clean-safe", action="store_true", help="Clean all safe junk categories to Recycle Bin")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be cleaned without deleting")

    args = parser.parse_args()

    if args.scan:
        run_cli_scan()
    elif args.clean_safe:
        run_cli_clean(dry_run=args.dry_run)
    else:
        try:
            from ui.app import start_app
            start_app()
        except (ImportError, RuntimeError, OSError) as e:
            print(f"[!] Unable to launch GUI: {e}")
            print("[*] Falling back to CLI scan:")
            run_cli_scan()



if __name__ == "__main__":
    main()
