from engine.scoring import score_lisibilite


def test_texte_clair_score_haut():
    assert score_lisibilite("le chat est sur la table") > 0.5


def test_texte_aleatoire_score_bas():
    assert score_lisibilite("x8f#9zQ!mP2kzz") < 0.5


def test_texte_vide():
    assert score_lisibilite("") == 0.0
