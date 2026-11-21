import hmac

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.auth import (
    auth_aktif,
    bersihkan_percobaan,
    buat_cookie_sesi,
    catat_gagal,
    hapus_cookie_sesi,
    kata_sandi,
    sesi_valid,
    terlalu_banyak,
    tujuan_aman,
)
from app.security import verifikasi_csrf
from app.templating import render

router = APIRouter(dependencies=[Depends(verifikasi_csrf)])


@router.get("/masuk")
def form_masuk(request: Request, next: str = "", keluar: str = ""):
    if not auth_aktif():
        return RedirectResponse("/", status_code=303)

    tujuan = tujuan_aman(next)
    if sesi_valid(request):
        return RedirectResponse(tujuan, status_code=303)

    return render(
        request,
        "masuk.html",
        tujuan=tujuan,
        error=None,
        pesan="Kamu sudah keluar." if keluar else "",
        judul_halaman="Masuk",
    )


@router.post("/masuk")
async def proses_masuk(request: Request):
    if not auth_aktif():
        return RedirectResponse("/", status_code=303)

    form = await request.form()
    tujuan = tujuan_aman((form.get("next") or "").strip())

    if terlalu_banyak(request):
        return render(
            request,
            "masuk.html",
            tujuan=tujuan,
            error="Terlalu banyak percobaan. Coba lagi dalam 15 menit.",
            pesan="",
            judul_halaman="Masuk",
            status_code=429,
        )

    dikirim = (form.get("sandi") or "").encode("utf-8")
    if hmac.compare_digest(dikirim, kata_sandi().encode("utf-8")):
        bersihkan_percobaan(request)
        response = RedirectResponse(tujuan, status_code=303)
        buat_cookie_sesi(request, response)
        return response

    catat_gagal(request)
    return render(
        request,
        "masuk.html",
        tujuan=tujuan,
        error="Kata sandi salah.",
        pesan="",
        judul_halaman="Masuk",
    )


@router.post("/keluar")
def keluar(request: Request):
    response = RedirectResponse("/masuk?keluar=1", status_code=303)
    hapus_cookie_sesi(response)
    return response
