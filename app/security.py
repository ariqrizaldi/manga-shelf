import hmac

from fastapi import HTTPException, Request


async def verifikasi_csrf(request: Request) -> None:
    """Double-submit cookie: token cookie harus sama dengan field/header."""
    if request.method != "POST":
        return

    token = getattr(request.state, "csrf", "")
    dikirim = request.headers.get("x-csrf-token")
    if not dikirim:
        tipe = request.headers.get("content-type", "")
        if tipe.startswith("application/x-www-form-urlencoded") or tipe.startswith(
            "multipart/form-data"
        ):
            form = await request.form()
            dikirim = form.get("csrf_token")

    if not dikirim or not token or not hmac.compare_digest(dikirim, token):
        raise HTTPException(
            status_code=403,
            detail="Sesi formulir kedaluwarsa. Muat ulang halaman lalu coba lagi.",
        )
