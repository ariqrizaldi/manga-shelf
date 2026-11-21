"""Salinan aman database SQLite, aman dijalankan saat aplikasi hidup.

Di container:
    docker compose exec -T app python scripts/backup.py

Menyimpan maksimal 14 salinan terakhir di folder yang sama dengan database
(default: /data/backup).
"""

import os
import sqlite3
import time
from pathlib import Path

DB = Path(os.environ.get("MANGA_DB", "/data/manga.db"))
TUJUAN = Path(os.environ.get("MANGA_BACKUP_DIR", DB.parent / "backup"))
SIMPAN = 14


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"Database tidak ditemukan: {DB}")

    TUJUAN.mkdir(parents=True, exist_ok=True)
    cap = time.strftime("%Y%m%d-%H%M%S")
    hasil = TUJUAN / f"manga-{cap}.db"

    with sqlite3.connect(DB) as sumber, sqlite3.connect(hasil) as salinan:
        sumber.backup(salinan)

    lama = sorted(TUJUAN.glob("manga-*.db"))
    for berkas in lama[:-SIMPAN]:
        berkas.unlink()

    print(hasil)


if __name__ == "__main__":
    main()
