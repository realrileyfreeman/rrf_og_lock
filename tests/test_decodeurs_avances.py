import base64
import gzip
import hashlib

from engine.decodeurs import gzip_dec, xor_dec, hash_dec


def test_gzip_round_trip():
    original = "bonjour le monde"
    compresse = gzip.compress(original.encode())
    encode = base64.b64encode(compresse).decode()

    assert gzip_dec.detecter(encode) > 0.5
    assert gzip_dec.decoder(encode) == original


def test_xor_round_trip():
    original = "le chat est content"
    cle = 0x42
    donnees = bytes(b ^ cle for b in original.encode())
    encode = donnees.decode("latin-1")

    resultat = xor_dec.decoder(encode)
    assert resultat == original


def test_hash_identifie_md5():
    empreinte = hashlib.md5(b"test").hexdigest()

    assert hash_dec.detecter(empreinte) > 0.0
    assert "MD5" in hash_dec.decoder(empreinte)


def test_xor_detecter_renvoie_un_float_dans_0_1():
    assert 0.0 <= xor_dec.detecter("le chat est content") <= 1.0
    assert xor_dec.detecter("ab") == 0.0
