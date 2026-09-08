import base64
import json

from engine.decodeurs import html_dec, unicode_dec, jwt_dec


def test_html_round_trip():
    encode = "5 &lt; 10"

    assert html_dec.detecter(encode) > 0.0
    assert html_dec.decoder(encode) == "5 < 10"


def test_unicode_round_trip():
    encode = "caf\\u00e9"

    assert unicode_dec.detecter(encode) > 0.0
    assert unicode_dec.decoder(encode) == "café"


def _b64url(donnees):
    return base64.urlsafe_b64encode(json.dumps(donnees).encode()).rstrip(b"=").decode()


def test_jwt_round_trip():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"utilisateur": "test"}
    token = f"{_b64url(header)}.{_b64url(payload)}.signature"

    assert jwt_dec.detecter(token) > 0.5
    resultat = json.loads(jwt_dec.decoder(token))
    assert resultat["payload"]["utilisateur"] == "test"
