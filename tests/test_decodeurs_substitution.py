from engine.decodeurs import rot_dec, binaire_dec, morse_dec


def test_rot13_retrouve_un_texte_connu():
    # "le chat" decale de 13 -> "yr pung"
    resultat = rot_dec.decoder("yr pung")
    assert resultat.lower() == "le chat"


def test_rot_detecter_renvoie_un_float_dans_0_1():
    assert 0.0 <= rot_dec.detecter("yr pung") <= 1.0
    assert rot_dec.detecter("1234") == 0.0


def test_binaire_round_trip():
    original = "hi"
    encode = " ".join(format(b, "08b") for b in original.encode())

    assert binaire_dec.detecter(encode) > 0.5
    assert binaire_dec.decoder(encode) == original


def test_morse_round_trip():
    encode = "... --- ..."

    assert morse_dec.detecter(encode) > 0.5
    assert morse_dec.decoder(encode) == "sos"
