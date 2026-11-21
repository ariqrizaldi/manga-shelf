import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlmodel import Session

from app.db import get_session
from app.routes.manga import _semua_view
from app.templating import render

router = APIRouter()


def _daftar(session: Session) -> list[dict]:
    views = _semua_view(session)
    return [v for v in views if v["kurang"] > 0 and v["dimiliki"] > 0]


def _baris_teks(v: dict) -> str:
    manga = v["manga"]
    return f"{manga.judul} ({v['dimiliki']}/{manga.total_volume or '?'}) — kurang {v['kurang']}: {v['kurang_terkompres']}"


@router.get("/daftar-kurang")
def halaman_daftar_kurang(
    request: Request,
    urut: str = "kurang",
    session: Session = Depends(get_session),
):
    daftar = _daftar(session)
    if urut == "judul":
        daftar.sort(key=lambda v: v["manga"].judul_norm)
    else:
        daftar.sort(key=lambda v: (v["kurang"], v["manga"].judul_norm))
        urut = "kurang"

    total_kurang = sum(v["kurang"] for v in daftar)
    teks_semua = "\n".join(_baris_teks(v) for v in daftar)
    return render(
        request,
        "daftar_kurang.html",
        daftar=daftar,
        urut=urut,
        total_kurang=total_kurang,
        teks_semua=teks_semua,
    )


@router.get("/daftar-kurang/unduh")
def unduh_daftar_kurang(
    format: str = "txt",
    session: Session = Depends(get_session),
):
    daftar = _daftar(session)
    daftar.sort(key=lambda v: (v["kurang"], v["manga"].judul_norm))
    tanggal = datetime.now().strftime("%Y%m%d")

    if format == "csv":
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer)
        writer.writerow(
            ["judul", "author", "total_volume", "dimiliki", "kurang", "volume_kurang"]
        )
        for v in daftar:
            writer.writerow(
                [
                    v["manga"].judul,
                    v["manga"].author or "",
                    v["manga"].total_volume,
                    v["dimiliki"],
                    v["kurang"],
                    v["kurang_terkompres"],
                ]
            )
        isi = "\ufeff" + buffer.getvalue()
        media = "text/csv; charset=utf-8"
        nama = f"mangashelf-daftar-kurang-{tanggal}.csv"
    else:
        baris = ["DAFTAR KURANG — MangaShelf", ""]
        for v in daftar:
            baris.append(_baris_teks(v))
        isi = "\n".join(baris) + "\n"
        media = "text/plain; charset=utf-8"
        nama = f"mangashelf-daftar-kurang-{tanggal}.txt"

    return Response(
        content=isi,
        media_type=media,
        headers={"Content-Disposition": f"attachment; filename={nama}"},
    )
