#!/usr/bin/env python3
"""
Scan HTML files in a directory and report all referenced media files
(images, GIFs, videos, etc.), indicating whether each exists on disk and is tracked in git.
"""

import re
import subprocess
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {'.png', '.gif', '.jpg', '.jpeg', '.svg', '.webp', '.ico', '.mp4', '.webm', '.ogg'}

# Match HTML attributes such as src="...", href="...", and poster="..."
ATTR_RE = re.compile(r'(?:src|href|poster)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

# Match common inline JavaScript object properties such as
# { src: '...', href: '...', poster: '...' }
JS_PROP_RE = re.compile(r'(?:src|href|poster)\s*:\s*["\']([^"\']+)["\']', re.IGNORECASE)


def is_git_tracked(file_path: Path, repo_root: Path) -> bool:
    """Check if a file is tracked in git."""
    try:
        rel_path = file_path.relative_to(repo_root)
        result = subprocess.run(
            ['git', 'ls-files', '--error-unmatch', str(rel_path)],
            cwd=repo_root,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def resolve_media_path(ref: str, base_dir: Path, repo_root: Path) -> Path:
    """Resolve a media reference against the HTML file or repository root."""
    clean_ref = ref.split('?', 1)[0]
    if clean_ref.startswith('/'):
        return (repo_root / clean_ref.lstrip('/')).resolve()
    return (base_dir / clean_ref).resolve()


def find_media_in_html(html_path: Path, repo_root: Path) -> list[dict]:
    """Return list of media references found in *html_path*."""
    text = html_path.read_text(encoding='utf-8', errors='replace')
    base_dir = html_path.parent
    results = []
    seen = set()

    for match in ATTR_RE.finditer(text):
        ref = match.group(1).strip()
        # Skip external URLs and data URIs
        if ref.startswith(('http://', 'https://', 'data:', '//', '#')):
            continue
        ext = Path(ref.split('?')[0]).suffix.lower()
        if ext not in MEDIA_EXTENSIONS:
            continue
        if ref in seen:
            continue
        seen.add(ref)

        abs_path = resolve_media_path(ref, base_dir, repo_root)
        tracked = is_git_tracked(abs_path, repo_root) if abs_path.exists() else None
        results.append({
            'ref': ref,
            'abs_path': abs_path,
            'exists': abs_path.exists(),
            'tracked': tracked,
        })

    for match in JS_PROP_RE.finditer(text):
        ref = match.group(1).strip()
        # Skip external URLs and data URIs
        if ref.startswith(('http://', 'https://', 'data:', '//', '#')):
            continue
        ext = Path(ref.split('?')[0]).suffix.lower()
        if ext not in MEDIA_EXTENSIONS:
            continue
        if ref in seen:
            continue
        seen.add(ref)

        abs_path = resolve_media_path(ref, base_dir, repo_root)
        tracked = is_git_tracked(abs_path, repo_root) if abs_path.exists() else None
        results.append({
            'ref': ref,
            'abs_path': abs_path,
            'exists': abs_path.exists(),
            'tracked': tracked,
        })

    return results


def check_html_files(root: str = '.') -> tuple[int, int]:
    root_path = Path(root).resolve()
    html_files = sorted(root_path.glob('**/*.html'))

    if not html_files:
        print('No HTML files found.')
        return 0, 0

    # Find git repo root
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=root_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        git_root = Path(result.stdout.strip()) if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, Exception):
        git_root = None

    total_missing = 0
    total_untracked = 0

    for html_file in html_files:
        rel_html = html_file.relative_to(root_path)
        media = find_media_in_html(html_file, git_root or root_path)

        if not media:
            print(f'\n[{rel_html}]  — no local media references')
            continue

        missing = [m for m in media if not m['exists']]
        ok      = [m for m in media if m['exists']]
        untracked = [m for m in media if m['tracked'] is False]
        total_missing += len(missing)
        total_untracked += len(untracked)

        print(f'\n[{rel_html}]  ({len(ok)} found, {len(missing)} MISSING, {len(untracked)} UNTRACKED)')
        for m in media:
            if not m['exists']:
                status = '  MISSING'
            elif m['tracked'] is False:
                status = '  UNTRACKED'
            elif m['tracked'] is True:
                status = '  TRACKED'
            else:
                status = '  UNKNOWN'
            print(f'  {status}  {m["ref"]}')

    print(f'\n{"="*60}')
    print(f'Total missing files: {total_missing}')
    if git_root:
        print(f'Total untracked files: {total_untracked}')

    return total_missing, total_untracked


if __name__ == '__main__':
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    total_missing, _ = check_html_files(root_dir)
    sys.exit(1 if total_missing else 0)
