#!/usr/bin/env python3
"""
Package the GTA 5 RP Suite & Mirror Legislation repository into ZIP archives:
1. Individual module plugins with top-level SKILL.md (ideal for Claude Desktop Settings -> Plugins -> Upload Plugin)
2. Full repository archive with .claude-plugin/plugin.json (for Claude Projects, Antigravity, and Custom GPTs)

Excludes .git, .archived, __pycache__, dist, virtual environments, and temporary files.
"""

from pathlib import Path
import zipfile

def package_single_module(module_dir: Path, output_zip: Path):
    exclude_dirs = {".git", ".archived", "__pycache__", ".venv", "venv", "dist"}
    exclude_files = {".DS_Store", "Thumbs.db"}
    
    count = 0
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(module_dir.rglob("*")):
            if item.is_file():
                rel_parts = set(item.relative_to(module_dir).parts)
                if any(ex in rel_parts for ex in exclude_dirs):
                    continue
                if item.name in exclude_files or item.suffix in (".pyc", ".pyo", ".zip"):
                    continue
                arcname = item.relative_to(module_dir)
                zf.write(item, arcname)
                count += 1
    size_mb = output_zip.stat().st_size / (1024 * 1024)
    print(f"  [OK] Module plugin: {output_zip.name} ({count} files, {size_mb:.2f} MB)")

def make_dist_zips():
    root = Path(__file__).resolve().parent.parent
    dist_dir = root / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    print("[*] Packaging individual Claude Desktop plugins (with top-level SKILL.md)...")
    modules = [
        "gta5rp-mirror-legislation",
        "gta5rp-forum-documents",
        "gta5rp-forum-navigation",
    ]
    for mod in modules:
        mod_path = root / mod
        if mod_path.is_dir():
            out_zip = dist_dir / f"{mod}.zip"
            package_single_module(mod_path, out_zip)
            
    print("\n[*] Packaging Full Suite archive (with .claude-plugin/plugin.json)...")
    suite_zip = dist_dir / "AISkill4gta5rp-Mirror.zip"
    exclude_dirs = {".git", ".archived", "__pycache__", ".venv", "venv", "dist"}
    exclude_files = {".DS_Store", "Thumbs.db"}
    
    count = 0
    with zipfile.ZipFile(suite_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(root.rglob("*")):
            if item.is_file():
                rel_parts = set(item.relative_to(root).parts)
                if any(ex in rel_parts for ex in exclude_dirs):
                    continue
                if item.name in exclude_files or item.suffix in (".pyc", ".pyo", ".zip") or item.name.startswith(".~"):
                    continue
                arcname = item.relative_to(root)
                zf.write(item, arcname)
                count += 1
                
    size_mb = suite_zip.stat().st_size / (1024 * 1024)
    print(f"  [OK] Full Suite archive: {suite_zip.name} ({count} files, {size_mb:.2f} MB)")
    print(f"\n[DONE] All archives ready in: {dist_dir}")

if __name__ == "__main__":
    make_dist_zips()
