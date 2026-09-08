import base64

from engine.decodeurs import base64_dec, base32_dec, hex_dec, url_dec


def test_base64_round_trip():
    original = "bonjour le monde"
    encode = base64.b64encode(original.encode()).decode()

    assert base64_dec.detecter(encode) > 0.5
    assert base64_dec.decoder(encode) == original


def test_base64_texte_non_base64():
    assert base64_dec.detecter("bonjour") == 0.0


def test_base32_round_trip():
    original = "salut"
    encode = base64.b32encode(original.encode()).decode()

    assert base32_dec.detecter(encode) > 0.5
    assert base32_dec.decoder(encode) == original


def test_hex_round_trip():
    original = "salut"
    encode = original.encode().hex()

    assert hex_dec.detecter(encode) > 0.5
    assert hex_dec.decoder(encode) == original


def test_url_round_trip():
    encode = "bonjour%20le%20monde"

    assert url_dec.detecter(encode) > 0.0
    assert url_dec.decoder(encode) == "bonjour le monde"


def test_url_sans_encodage():
    assert url_dec.detecter("bonjour") == 0.0
