"""Isi database dengan tiga contoh dari PRD. Jalankan: python seed.py"""

import sys
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlmodel import Session, SQLModel, select

from app.db import engine, init_db
from app.models import Manga, Volume
from app.rentang import parse_rentang
from app.utils import normalisasi_judul

CONTOH = [
    {
        "judul": "One Piece",
        "author": "Eiichiro Oda",
        "status_rilis": "ongoing",
        "total_volume": 112,
        "status_baca": "sedang",
        "volume_dimiliki": "1-105",
        "rating": 5,
        "catatan": "Kurang vol 106-112.",
        "cover_url": "",
    },
    {
        "judul": "Attack on Titan",
        "author": "Hajime Isayama",
        "status_rilis": "tamat",
        "total_volume": 34,
        "status_baca": "selesai",
        "volume_dimiliki": "1-34",
        "rating": 5,
        "catatan": "Lengkap.",
        "cover_url": "",
    },
    {
        "judul": "Naruto",
        "author": "Masashi Kishimoto",
        "status_rilis": "tamat",
        "total_volume": 72,
        "status_baca": "belum",
        "volume_dimiliki": "1-24, 30-42, 55-72",
        "rating": 4,
        "catatan": "Contoh koleksi bolong: kurang 25-29 dan 43-54.",
        "cover_url": "",
    },
]


def main() -> None:
    force = "--force" in sys.argv
    init_db()

    if force:
        SQLModel.metadata.drop_all(engine)
        init_db()

    with Session(engine) as session:
        if session.exec(select(Manga)).first() is not None:
            print("Database sudah berisi data. Seed dilewati (pakai --force untuk mengulang).")
            return

        session.exec(delete(Volume))
        session.exec(delete(Manga))
        session.commit()

        now = datetime.now(timezone.utc)
        for data in CONTOH:
            manga = Manga(
                judul=data["judul"],
                judul_norm=normalisasi_judul(data["judul"]),
                author=data["author"],
                status_rilis=data["status_rilis"],
                total_volume=data["total_volume"],
                status_baca=data["status_baca"],
                rating=data["rating"],
                catatan=data["catatan"],
                cover_url=data["cover_url"] or None,
                tanggal_tambah=now,
                tanggal_update=now,
            )
            session.add(manga)
            session.commit()
            session.refresh(manga)
            for nomor in sorted(parse_rentang(data["volume_dimiliki"])):
                session.add(Volume(manga_id=manga.id, nomor=nomor))
            session.commit()
            print(f"  + {manga.judul}: {data['volume_dimiliki']}")

    print("Seed selesai.")


if __name__ == "__main__":
    main()
