import base64
import gzip
import zlib

ENTETES_ZLIB = (b"\x78\x9c", b"\x78\x01", b"\x78\xda")


def detecter(texte):
    t = texte.strip()
    try:
        brut = base64.b64decode(t, validate=True)
    except Exception:
        return 0.0
    if brut[:2] == b"\x1f\x8b" or brut[:2] in ENTETES_ZLIB:
        return 0.8
    return 0.0


def decoder(texte):
    brut = base64.b64decode(texte.strip())
    try:
        return gzip.decompress(brut).decode("utf-8", errors="replace")
    except OSError:
        return zlib.decompress(brut).decode("utf-8", errors="replace")
