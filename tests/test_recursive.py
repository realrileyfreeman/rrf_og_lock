import base64

from engine.recursive import auto_decode, detect_layer


def _aplatir(noeud):
    textes = [noeud.texte]
    for enfant in noeud.enfants:
        textes.extend(_aplatir(enfant))
    return textes


def test_detect_layer_trouve_base64():
    encode = base64.b64encode(b"bonjour").decode()
    candidats = detect_layer(encode)

    noms = [c.decodeur for c in candidats]
    assert "base64" in noms


def test_auto_decode_multicouche_hex_puis_base64():
    original = "bonjour le monde"
    etape1 = original.encode().hex()
    etape2 = base64.b64encode(etape1.encode()).decode()

    arbre = auto_decode(etape2)

    assert original in _aplatir(arbre)


def test_auto_decode_respecte_profondeur_max():
    arbre = auto_decode("xyz123", profondeur_max=0)
    assert arbre.enfants == []
