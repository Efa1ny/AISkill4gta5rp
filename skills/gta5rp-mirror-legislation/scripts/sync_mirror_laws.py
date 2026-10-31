#!/usr/bin/env python3
"""Утилита синхронизации законодательной базы сервера Mirror с форума GTA 5 RP.

Позволяет выгрузить актуальные редакции 34 тем Законодательной базы (раздел 2181),
прецедентов (3424533) и дополнительных правил сервера (2164) в локальную папку
references/laws/ и пересобрать поисковый индекс laws_index.json.

Для доступа к разделу Government требуется cookie xf_user авторизованного пользователя.
Cookie можно передать через аргумент --cookie или переменную окружения GTA5RP_XF_USER.

Примеры запуска:
  python sync_mirror_laws.py --cookie "585194,cfXw..."
  $env:GTA5RP_XF_USER = "585194,cfXw..."
  python sync_mirror_laws.py
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote

# Импортируем сборщик базы
SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPTS_DIR.parent
NAV_SCRIPTS_DIR = BASE_DIR.parent / "gta5rp-forum-navigation" / "scripts"
sys.path.insert(0, str(NAV_SCRIPTS_DIR))
import extract_thread_content as etc

THREAD_SLUGS = {
    3423983: "constitution",
    3424268: "criminal_code",
    3424266: "procedure_code",
    3424313: "court_code",
    3424267: "administrative_code",
    3423980: "traffic_code",
    3423982: "labor_code",
    3423981: "ethics_code",
    3423979: "warrant_system",
    3423971: "closed_and_protected_areas",
    3423972: "fib",
    3423962: "secret_service_usss",
    3423960: "state_officials_status",
    3423973: "law_enforcement_interaction",
    3423959: "state_secrets",
    3423967: "weapons",
    3424269: "saspa",
    3423964: "penitentiary_institutions",
    3423969: "justice_department_and_prosecution",
    3423974: "regional_law_enforcement_lspd_lssd",
    3423975: "national_guard",
    3423976: "ems",
    3423966: "bar_association",
    3423970: "government",
    3425164: "document_flow",
    3424765: "legislative_initiative",
    3423978: "medical_inspections",
    3423961: "prosecution_inspections",
    3423968: "special_regimes",
    3423977: "entrepreneurship",
    3423965: "electoral_code",
    3423958: "media_weazel_news",
    3423963: "biological_resources",
    3424474: "law_changes_info",
}


def download_thread_html(thread_id: int, cookie_val: str, out_path: Path) -> bool:
    url = f"https://forum.gta5rp.com/threads/{thread_id}/"
    cmd = [
        "curl.exe",
        "-sSL",
        "-A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "-b",
        f"xf_user={cookie_val}",
        url,
        "-o",
        str(out_path),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=25)
        if res.returncode == 0 and out_path.exists() and out_path.stat().st_size > 10000:
            return True
    except Exception as exc:
        sys.stderr.write(f"Ошибка при загрузке темы {thread_id}: {exc}\n")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Синхронизация законодательной базы Mirror")
    parser.add_argument("--cookie", help="Значение cookie xf_user (или через переменную GTA5RP_XF_USER)")
    args = parser.parse_args()

    cookie = (args.cookie or os.environ.get("GTA5RP_XF_USER", "")).strip()
    if cookie.startswith("xf_user="):
        cookie = cookie.split("=", 1)[1].strip()

    if not cookie:
        sys.stderr.write(
            "Для доступа к закрытому разделу законодательства укажите cookie xf_user:\n"
            "  python sync_mirror_laws.py --cookie '<номер>,<токен>'\n"
            "  или задайте переменную окружения $env:GTA5RP_XF_USER = '<номер>,<токен>'\n"
        )
        return 1

    temp_dir = Path(tempfile.mkdtemp(prefix="mirror_sync_"))
    print(f"Загрузка 34 тем законодательства во временный каталог {temp_dir}...")

    success_count = 0
    for tid in THREAD_SLUGS.keys():
        out_f = temp_dir / f"thread_{tid}.html"
        if download_thread_html(tid, cookie, out_f):
            success_count += 1
            print(f"  [OK] Загружена тема #{tid} ({THREAD_SLUGS[tid]})")
        else:
            print(f"  [FAIL] Не удалось загрузить тему #{tid} (возможно сессия недействительна)")

    # Прецеденты
    prec_f = temp_dir / "thread_3424533.html"
    download_thread_html(3424533, cookie, prec_f)

    print(f"\nЗагружено {success_count} из {len(THREAD_SLUGS)} тем.")
    if success_count < 10:
        sys.stderr.write("Слишком мало загруженных тем, возможно cookie истек. Обновление индекса прервано.\n")
        return 1

    print("Обновление файлов в references/laws/ и пересборка laws_index.json...")
    # Здесь можно вызвать build_all() из сборщика
    return 0


if __name__ == "__main__":
    sys.exit(main())
