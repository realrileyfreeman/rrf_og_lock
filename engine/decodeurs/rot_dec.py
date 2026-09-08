import string

from engine.scoring import score_lisibilite

ALPHABET_MIN = string.ascii_lowercase
ALPHABET_MAJ = string.ascii_uppercase


def _decaler(texte, n):
    resultat = []
    for c in texte:
        if c in ALPHABET_MIN:
            resultat.append(ALPHABET_MIN[(ALPHABET_MIN.index(c) - n) % 26])
        elif c in ALPHABET_MAJ:
            resultat.append(ALPHABET_MAJ[(ALPHABET_MAJ.index(c) - n) % 26])
        else:
            resultat.append(c)
    return "".join(resultat)


def detecter(texte):
    lettres = sum(1 for c in texte if c.isalpha())
    if lettres == 0:
        return 0.0
    return 0.3


def decoder(texte):
    meilleur = texte
    meilleur_score = -1
    for n in range(26):
        candidat = _decaler(texte, n)
        s = score_lisibilite(candidat)
        if s >= meilleur_score:
            meilleur_score = s
            meilleur = candidat
    return meilleur
