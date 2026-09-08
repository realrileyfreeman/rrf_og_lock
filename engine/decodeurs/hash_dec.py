import re

LONGUEURS = {32: "MD5", 40: "SHA1", 64: "SHA256"}


def detecter(texte):
    t = texte.strip()
    if len(t) in LONGUEURS and re.fullmatch(r"[0-9a-fA-F]+", t):
        return 0.5
    return 0.0


def decoder(texte):
    t = texte.strip()
    nom = LONGUEURS.get(len(t), "hash")
    return f"[{nom} detecte, non reversible] {t}"
