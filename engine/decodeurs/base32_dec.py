import base64
import re

PATTERN = re.compile(r"^[A-Z2-7]+=*$")


def detecter(texte):
    t = texte.strip().upper()
    if len(t) < 8 or len(t) % 8 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().upper()
    manquant = len(t) % 8
    if manquant:
        t += "=" * (8 - manquant)
    brut = base64.b32decode(t)
    return brut.decode("utf-8", errors="replace")
