import base64

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_decode_auto():
    encode = base64.b64encode(b"bonjour").decode()
    reponse = client.post("/decode", json={"texte": encode})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["decodeur"] == "entree"
    assert len(corps["enfants"]) > 0


def test_decode_step():
    encode = base64.b64encode(b"bonjour").decode()
    reponse = client.post("/decode/step", json={"texte": encode})

    assert reponse.status_code == 200
    noms = [c["decodeur"] for c in reponse.json()]
    assert "base64" in noms


def test_liste_decodeurs():
    reponse = client.get("/decodeurs")

    assert reponse.status_code == 200
    assert "base64" in reponse.json()
