import base64
import json
import re

PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def detecter(texte):
    if PATTERN.match(texte.strip()):
        return 0.9
    return 0.0


def _decoder_partie(partie):
    manquant = len(partie) % 4
    if manquant:
        partie += "=" * (4 - manquant)
    brut = base64.urlsafe_b64decode(partie)
    return json.loads(brut)


def decoder(texte):
    header, payload, _signature = texte.strip().split(".")
    contenu = {
        "header": _decoder_partie(header),
        "payload": _decoder_partie(payload),
    }
    return json.dumps(contenu, ensure_ascii=False)
