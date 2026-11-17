#!/usr/bin/env python3
"""Синхронизирует дубли плагина с каноническими папками.

Канон (правь только его):
  commands/            — слэш-команды плагина
  skills/<модуль>/     — модули (SKILL.md, references, scripts)

Копии (их читают Gemini CLI / Antigravity и архивы отдельных модулей), перезаписываются целиком:
  commands/                       → skills/gta5rp-mirror-legislation/commands/
  skills/<модуль>/                → <модуль>/

Запуск:
  python scripts/sync_copies.py           # перезаписать копии
  python scripts/sync_copies.py --check   # только проверить: exit 1, если копии разошлись с каноном
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
MODULES = ("gta5rp-forum-documents", "gta5rp-forum-navigation", "gta5rp-mirror-legislation")
# Порядок важен: команды попадают в skills/ до того, как skills/ копируется в корень.
PAIRS = [(ROOT / "commands", ROOT / "skills" / "gta5rp-mirror-legislation" / "commands")] + [
    (ROOT / "skills" / m, ROOT / m) for m in MODULES
]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def tree(path: Path) -> dict[str, bytes]:
    """Файлы папки → содержимое; CRLF приравнен к LF (git autocrlf на Windows)."""
    if not path.exists():
        return {}
    return {
        p.relative_to(path).as_posix(): p.read_bytes().replace(b"\r\n", b"\n")
        for p in sorted(path.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def main(argv: list[str]) -> int:
    check = "--check" in argv
    dirty = []
    for src, dst in PAIRS:
        if tree(src) == tree(dst):
            continue
        dirty.append(dst.relative_to(ROOT).as_posix())
        if not check:
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst, ignore=IGNORE)

    if not dirty:
        print("Копии совпадают с каноном.")
        return 0
    if check:
        print("Копии разошлись с каноном (запусти python scripts/sync_copies.py):\n  " + "\n  ".join(dirty))
        return 1
    print("Перезаписаны копии:\n  " + "\n  ".join(dirty))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
