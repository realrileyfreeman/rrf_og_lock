import re

PATTERN = re.compile(r"^[01]+$")


def detecter(texte):
    t = texte.strip().replace(" ", "")
    if len(t) < 8 or len(t) % 8 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().replace(" ", "")
    octets = [t[i:i + 8] for i in range(0, len(t), 8)]
    brut = bytes(int(o, 2) for o in octets)
    return brut.decode("utf-8", errors="replace")
