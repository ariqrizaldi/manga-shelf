from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _sekarang() -> datetime:
    return datetime.now(timezone.utc)


class Manga(SQLModel, table=True):
    __tablename__ = "manga"

    id: Optional[int] = Field(default=None, primary_key=True)
    judul: str = Field(max_length=200)
    judul_norm: str = Field(default="", index=True)
    author: Optional[str] = Field(default=None, max_length=200)
    status_rilis: str = Field(default="ongoing")  # ongoing | tamat
    total_volume: int = Field(default=0)
    status_baca: str = Field(default="belum")  # belum | sedang | selesai | dihentikan
    rating: Optional[int] = Field(default=None)
    catatan: Optional[str] = None
    cover_url: Optional[str] = None
    tanggal_tambah: datetime = Field(default_factory=_sekarang)
    tanggal_update: datetime = Field(default_factory=_sekarang)


class Volume(SQLModel, table=True):
    __tablename__ = "volume"

    manga_id: int = Field(foreign_key="manga.id", primary_key=True, ondelete="CASCADE")
    nomor: int = Field(primary_key=True)
