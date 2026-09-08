import re

PATTERN = re.compile(r"^[0-9a-fA-F]+$")


def detecter(texte):
    t = texte.strip().replace(" ", "")
    if len(t) < 2 or len(t) % 2 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().replace(" ", "")
    brut = bytes.fromhex(t)
    return brut.decode("utf-8", errors="replace")
