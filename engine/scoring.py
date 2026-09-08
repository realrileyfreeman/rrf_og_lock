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
        connus = sum(1 for m in mots if m in MOTS_COURANTS)
        ratio_mots = connus / len(mots)
    else:
        ratio_mots = 0.0

    return 0.4 * ratio_imprimable + 0.6 * ratio_mots
