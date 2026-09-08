# RRF OG LOCK

Outil de décodage automatique et récursif multicouche, réalisé dans le cadre
d'un projet de master.

Étant donné une chaîne de texte, l'outil détecte quel encodage a été utilisé
(base64, hex, ROT13, morse, binaire, URL encoding, entités HTML, échappement
unicode, JWT, gzip/zlib+base64, XOR à clé courte, ...), la décode, puis répète
l'opération sur le résultat jusqu'à obtenir du texte clair.

## Installation

```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

## Lancer l'API

```bash
uvicorn api.main:app --reload
```

## Lancer le front

```bash
cd frontend
npm run dev
```

## Utiliser la CLI

```bash
python -m cli "Ym9uam91cg=="
```

## Lancer les tests

```bash
pytest -v
```

## Structure du projet

- `engine/` : moteur de décodage (pur Python, sans dépendance web)
- `api/` : API FastAPI qui expose le moteur
- `cli/` : interface en ligne de commande
- `frontend/` : interface web React
- `tests/` : tests pytest
