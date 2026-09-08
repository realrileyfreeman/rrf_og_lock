import sys

from engine.recursive import auto_decode


def afficher(noeud, indent=0):
    prefixe = "  " * indent
    print(f"{prefixe}[{noeud.decodeur}] (lisibilite={noeud.score_lisibilite:.2f}) {noeud.texte!r}")
    for enfant in noeud.enfants:
        afficher(enfant, indent + 1)


def main():
    if len(sys.argv) < 2:
        print('Usage: python -m cli "texte a decoder"')
        sys.exit(1)
    texte = sys.argv[1]
    arbre = auto_decode(texte)
    afficher(arbre)


if __name__ == "__main__":
    main()
