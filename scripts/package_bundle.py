#!/usr/bin/env python3
"""
Package the entire GTA 5 RP Suite & Mirror Legislation repository into a clean ZIP archive
ready for upload to Claude Projects, ChatGPT Custom GPTs, or offline sharing.

Excludes .git, .archived, __pycache__, dist, virtual environments, and temporary files.
"""

from pathlib import Path
import zipfile


def make_dist_zip():
  root = Path(__file__).resolve().parent.parent
  dist_dir = root / "dist"
  dist_dir.mkdir(exist_ok=True)
  zip_path = dist_dir / "AISkill4gta5rp-Mirror.zip"

  exclude_dirs = {".git", ".archived", "__pycache__", ".venv", "venv", "dist"}
  exclude_files = {".DS_Store", "Thumbs.db"}

  count = 0
  with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in sorted(root.rglob("*")):
      if item.is_file():
        rel_parts = set(item.relative_to(root).parts)
        if any(ex in rel_parts for ex in exclude_dirs):
          continue
        if (
            item.name in exclude_files
            or item.suffix in (".pyc", ".pyo", ".zip")
            or item.name.startswith(".~")
        ):
          continue
        arcname = item.relative_to(root)
        zf.write(item, arcname)
        count += 1

  size_mb = zip_path.stat().st_size / (1024 * 1024)
  print(f"[OK] Distribution archive created successfully!")
  print(f"     Path:     {zip_path}")
  print(f"     Files:    {count}")
  print(f"     Size:     {size_mb:.2f} MB")


if __name__ == "__main__":
  make_dist_zip()
