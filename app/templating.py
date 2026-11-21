from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.auth import auth_aktif
from app.utils import inisial

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
templates.env.globals["inisial"] = inisial


def render(request, nama: str, status_code: int = 200, **konteks):
    konteks.setdefault("csrf_token", getattr(request.state, "csrf", ""))
    konteks.setdefault("auth_aktif", auth_aktif())
    response = templates.TemplateResponse(
        request=request,
        name=nama,
        context=konteks,
        status_code=status_code,
    )
    response.headers.setdefault("Cache-Control", "no-store")
    return response
