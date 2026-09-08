import base64
import re

PATTERN = re.compile(r"^[A-Za-z0-9+/_-]+={0,2}$")


def detecter(texte):
    t = texte.strip()
    if len(t) < 4 or len(t) % 4 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.7


def decoder(texte):
    t = texte.strip().replace("-", "+").replace("_", "/")
    manquant = len(t) % 4
    if manquant:
        t += "=" * (4 - manquant)
    brut = base64.b64decode(t)
    return brut.decode("utf-8", errors="replace")
