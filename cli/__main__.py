import sys

from engine.recursive import auto_decode


def afficher(noeud, indent=0):
    prefixe = "  " * indent
    print(f"{prefixe}[{noeud.decodeur}] (lisibilite={noeud.score_lisibilite:.2f}) {noeud.texte!r}")
    for enfant in noeud.enfants:
        afficher(enfant, indent + 1)


def meilleure_feuille(noeud):
    if not noeud.enfants:
        return noeud
    return max((meilleure_feuille(e) for e in noeud.enfants), key=lambda n: n.score_lisibilite)


def main():
    if len(sys.argv) < 2:
        print('Usage: python -m cli "texte a decoder"')
        sys.exit(1)
    texte = sys.argv[1]
    arbre = auto_decode(texte)
    afficher(arbre)
    meilleure = meilleure_feuille(arbre)
    print(f"Meilleur resultat : {meilleure.texte!r} (lisibilite={meilleure.score_lisibilite:.2f})")


if __name__ == "__main__":
    main()
