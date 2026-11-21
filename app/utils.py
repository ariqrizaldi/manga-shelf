import re
import unicodedata


def normalisasi_judul(judul: str) -> str:
    teks = unicodedata.normalize("NFKD", judul or "").lower()
    teks = re.sub(r"[^a-z0-9]+", " ", teks)
    return re.sub(r"\s+", " ", teks).strip()


def inisial(judul: str) -> str:
    kata = [k for k in (judul or "").split() if k]
    if not kata:
        return "?"
    if len(kata) == 1:
        return kata[0][:2].upper()
    return (kata[0][0] + kata[1][0]).upper()
