from engine.scoring import score_lisibilite


def _xor(donnees, cle):
    return bytes(b ^ cle for b in donnees)


def detecter(texte):
    if len(texte) < 4:
        return 0.0
    return 0.2


def decoder(texte):
    donnees = texte.encode("latin-1", errors="replace")
    meilleur = texte
    meilleur_score = -1
    for cle in range(256):
        resultat = _xor(donnees, cle)
        try:
            decode = resultat.decode("utf-8")
        except UnicodeDecodeError:
            continue
        s = score_lisibilite(decode)
        if s >= meilleur_score:
            meilleur_score = s
            meilleur = decode
    return meilleur
