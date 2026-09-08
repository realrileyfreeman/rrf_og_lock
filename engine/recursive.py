from engine.decodeurs import TOUS
from engine.scoring import score_lisibilite
from engine.types import Candidat

SEUIL_DETECTION = 0.2
SEUIL_LISIBLE = 0.8
MAX_BRANCHES = 3


def detect_layer(texte):
    candidats = []
    for nom, module in TOUS:
        try:
            score = module.detecter(texte)
        except Exception:
            score = 0.0
        if score < SEUIL_DETECTION:
            continue
        try:
            resultat = module.decoder(texte)
        except Exception:
            continue
        candidats.append(Candidat(
            decodeur=nom,
            score_detection=score,
            texte=resultat,
            score_lisibilite=score_lisibilite(resultat),
        ))
    candidats.sort(key=lambda c: c.score_lisibilite, reverse=True)
    return candidats


def auto_decode(texte, profondeur_max=10):
    racine = Candidat(
        decodeur="entree",
        score_detection=1.0,
        texte=texte,
        score_lisibilite=score_lisibilite(texte),
    )
    _explorer(racine, profondeur_max)
    return racine


def _explorer(noeud, profondeur_restante):
    if profondeur_restante <= 0:
        return
    if noeud.score_lisibilite >= SEUIL_LISIBLE:
        return
    candidats = detect_layer(noeud.texte)
    noeud.enfants = candidats[:MAX_BRANCHES]
    for enfant in noeud.enfants:
        _explorer(enfant, profondeur_restante - 1)
