import re

MOTS_COURANTS = {
    "le", "la", "les", "de", "des", "un", "une", "et", "est", "que", "pour",
    "dans", "sur", "avec", "ne", "pas", "je", "tu", "il", "elle", "nous",
    "the", "and", "is", "of", "to", "in", "it", "you", "that", "this",
    "are", "was", "for", "on", "with",
}


def score_lisibilite(texte):
    if not texte:
        return 0.0

    imprimables = sum(1 for c in texte if c.isprintable())
    ratio_imprimable = imprimables / len(texte)

    mots = re.findall(r"[a-zA-ZÀ-ÿ]+", texte.lower())
    if mots:
        # ponderation par longueur : un stopword court qui matche par hasard
        # ne doit pas dominer le score comme le ferait un ratio par nombre de mots
        connus_mots = [m for m in mots if m in MOTS_COURANTS]
        ratio_mots = sum(len(m) for m in connus_mots) / sum(len(m) for m in mots)
    else:
        ratio_mots = 0.0

    return 0.4 * ratio_imprimable + 0.6 * ratio_mots
