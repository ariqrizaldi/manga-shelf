import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlmodel import Session

from app.db import DB_PATH, get_session
from app.rentang import kompres_rentang
from app.routes.manga import _semua_view
from app.templating import render

router = APIRouter()


@router.get("/pengaturan")
def halaman_pengaturan(
    request: Request,
    session: Session = Depends(get_session),
):
    views = _semua_view(session)
    return render(
        request,
        "pengaturan.html",
        total_judul=len(views),
        total_volume=sum(v["dimiliki"] for v in views),
        total_kurang=sum(v["kurang"] for v in views),
        lokasi_db=DB_PATH.as_posix(),
    )


def _data_ekspor(session: Session) -> list[dict]:
    hasil = []
    for v in _semua_view(session):
        manga = v["manga"]
        volume = sorted(v["dimiliki_set"])
        hasil.append(
            {
                "judul": manga.judul,
                "author": manga.author,
                "status_rilis": manga.status_rilis,
                "total_volume": manga.total_volume,
                "status_baca": manga.status_baca,
                "rating": manga.rating,
                "catatan": manga.catatan,
                "cover_url": manga.cover_url,
                "volume_dimiliki": volume,
                "volume_dimiliki_rentang": kompres_rentang(volume),
                "volume_kurang": v["kurang_nomor"],
                "volume_kurang_rentang": v["kurang_terkompres"],
                "tanggal_tambah": manga.tanggal_tambah.isoformat(timespec="seconds"),
                "tanggal_update": manga.tanggal_update.isoformat(timespec="seconds"),
            }
        )
    return hasil


@router.get("/ekspor/json")
def ekspor_json(session: Session = Depends(get_session)):
    data = {
        "aplikasi": "MangaShelf",
        "versi": 1,
        "diekspor": datetime.now().isoformat(timespec="seconds"),
        "jumlah_judul": None,
        "judul": _data_ekspor(session),
    }
    data["jumlah_judul"] = len(data["judul"])
    isi = json.dumps(data, ensure_ascii=False, indent=2)
    nama = f"mangashelf-{datetime.now():%Y%m%d}.json"
    return Response(
        content=isi,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nama}"},
    )


@router.get("/ekspor/csv")
def ekspor_csv(session: Session = Depends(get_session)):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "judul",
            "author",
            "status_rilis",
            "total_volume",
            "status_baca",
            "rating",
            "catatan",
            "cover_url",
            "volume_dimiliki",
            "volume_kurang",
            "tanggal_tambah",
        ]
    )
    for item in _data_ekspor(session):
        writer.writerow(
            [
                item["judul"],
                item["author"] or "",
                item["status_rilis"],
                item["total_volume"],
                item["status_baca"],
                item["rating"] or "",
                item["catatan"] or "",
                item["cover_url"] or "",
                item["volume_dimiliki_rentang"],
                item["volume_kurang_rentang"],
                item["tanggal_tambah"],
            ]
        )
    isi = "\ufeff" + buffer.getvalue()
    nama = f"mangashelf-{datetime.now():%Y%m%d}.csv"
    return Response(
        content=isi,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nama}"},
    )
