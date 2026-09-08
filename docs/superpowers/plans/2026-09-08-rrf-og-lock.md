# RRF OG LOCK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Outil de décodage automatique et récursif multicouche (base64, hex, rot13, morse, etc.) avec API Python, front React et CLI.

**Architecture:** Un cœur de logique pure Python (`engine/`) partagé par une API FastAPI, une CLI et les tests. Chaque encodage est un module avec `detecter(texte) -> float` et `decoder(texte) -> str`. Le moteur explore récursivement les couches détectées et construit un arbre de candidats.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, pytest, React + Vite.

**Spec:** `docs/superpowers/specs/2026-09-08-rrf-og-lock-design.md`

## Global Constraints

- Interface utilisateur (front) entièrement en français.
- Code et commentaires style étudiant de master : noms de variables/fonctions en français, commentaires rares (uniquement quand une intention n'est pas évidente), pas de docstrings.
- Aucune attribution IA dans les messages de commit.
- Pas de DB, pas d'authentification (stateless).
- Profondeur de récursion max par défaut : 10 (paramétrable).
- Le XOR est bruteforcé sur clé 1 octet uniquement (256 possibilités) pour rester rapide — simplification par rapport à "1 à 4 octets" du spec initial, notée ici pour traçabilité.

---

### Task 1 : Squelette du dépôt

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `conftest.py`
- Create: `LICENSE`
- Create: `engine/__init__.py`
- Create: `api/__init__.py`
- Create: `cli/__init__.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Produces: structure de dossiers vide prête à accueillir le code des tâches suivantes.

- [ ] **Step 1: Créer `.gitignore`**

```
__pycache__/
*.pyc
.venv/
venv/
node_modules/
dist/
.env
```

- [ ] **Step 2: Créer `requirements.txt`**

```
fastapi
uvicorn[standard]
pytest
```

- [ ] **Step 3: Créer `conftest.py` à la racine (vide)**

Fichier vide : permet à pytest d'ajouter la racine du dépôt à `sys.path` pour que `import engine` fonctionne depuis `tests/`.

```python
```

- [ ] **Step 4: Créer `LICENSE` (MIT)**

```
MIT License

Copyright (c) 2026 Omar Camara

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Créer les `__init__.py` vides**

`engine/__init__.py`, `api/__init__.py`, `cli/__init__.py`, `tests/__init__.py` : fichiers vides.

- [ ] **Step 6: Commit**

```bash
git add .gitignore requirements.txt conftest.py LICENSE engine/__init__.py api/__init__.py cli/__init__.py tests/__init__.py
git commit -m "Squelette du depot"
```

---

### Task 2 : Types et heuristique de lisibilité

**Files:**
- Create: `engine/types.py`
- Create: `engine/scoring.py`
- Test: `tests/test_scoring.py`

**Interfaces:**
- Produces: `Candidat` (dataclass avec champs `decodeur: str`, `score_detection: float`, `texte: str`, `score_lisibilite: float`, `enfants: list[Candidat]`) ; `score_lisibilite(texte: str) -> float`.

- [ ] **Step 1: Écrire les tests de `score_lisibilite`**

`tests/test_scoring.py` :

```python
from engine.scoring import score_lisibilite


def test_texte_clair_score_haut():
    assert score_lisibilite("le chat est sur la table") > 0.5


def test_texte_aleatoire_score_bas():
    assert score_lisibilite("x8f#9zQ!mP2kzz") < 0.5


def test_texte_vide():
    assert score_lisibilite("") == 0.0
```

- [ ] **Step 2: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_scoring.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'engine.scoring'`)

- [ ] **Step 3: Écrire `engine/types.py`**

```python
from dataclasses import dataclass, field


@dataclass
class Candidat:
    decodeur: str
    score_detection: float
    texte: str
    score_lisibilite: float
    enfants: list["Candidat"] = field(default_factory=list)
```

- [ ] **Step 4: Écrire `engine/scoring.py`**

```python
import re

MOTS_COURANTS = {
    "le", "la", "les", "de", "des", "un", "une", "et", "est", "que", "pour",
    "dans", "sur", "avec", "ne", "pas", "je", "tu", "il", "elle", "nous",
    "the", "and", "is", "of", "to", "in", "it", "you", "that", "this",
    "are", "was", "for", "on", "with",
}


def score_lisibilite(texte):
    if not texte:
        return 0.0

    imprimables = sum(1 for c in texte if c.isprintable())
    ratio_imprimable = imprimables / len(texte)

    mots = re.findall(r"[a-zA-ZÀ-ÿ]+", texte.lower())
    if mots:
        connus = sum(1 for m in mots if m in MOTS_COURANTS)
        ratio_mots = connus / len(mots)
    else:
        ratio_mots = 0.0

    return 0.6 * ratio_imprimable + 0.4 * ratio_mots
```

- [ ] **Step 5: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_scoring.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add engine/types.py engine/scoring.py tests/test_scoring.py
git commit -m "Ajout du score de lisibilite et du type Candidat"
```

---

### Task 3 : Décodeurs simples texte<->texte (base64, base32, hex, url)

**Files:**
- Create: `engine/decodeurs/__init__.py` (fichier vide à ce stade, rempli en tâche 7)
- Create: `engine/decodeurs/base64_dec.py`
- Create: `engine/decodeurs/base32_dec.py`
- Create: `engine/decodeurs/hex_dec.py`
- Create: `engine/decodeurs/url_dec.py`
- Test: `tests/test_decodeurs_simples.py`

**Interfaces:**
- Consumes: rien.
- Produces: chaque module expose `detecter(texte: str) -> float` et `decoder(texte: str) -> str`, convention reprise par tous les décodeurs suivants.

- [ ] **Step 1: Créer `engine/decodeurs/__init__.py` vide**

```python
```

- [ ] **Step 2: Écrire les tests**

`tests/test_decodeurs_simples.py` :

```python
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
```

- [ ] **Step 3: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_decodeurs_simples.py -v`
Expected: FAIL (modules manquants)

- [ ] **Step 4: Écrire `engine/decodeurs/base64_dec.py`**

```python
import base64
import re

PATTERN = re.compile(r"^[A-Za-z0-9+/_-]+={0,2}$")


def detecter(texte):
    t = texte.strip()
    if len(t) < 4 or len(t) % 4 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.7


def decoder(texte):
    t = texte.strip().replace("-", "+").replace("_", "/")
    manquant = len(t) % 4
    if manquant:
        t += "=" * (4 - manquant)
    brut = base64.b64decode(t)
    return brut.decode("utf-8", errors="replace")
```

- [ ] **Step 5: Écrire `engine/decodeurs/base32_dec.py`**

```python
import base64
import re

PATTERN = re.compile(r"^[A-Z2-7]+=*$")


def detecter(texte):
    t = texte.strip().upper()
    if len(t) < 8 or len(t) % 8 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().upper()
    manquant = len(t) % 8
    if manquant:
        t += "=" * (8 - manquant)
    brut = base64.b32decode(t)
    return brut.decode("utf-8", errors="replace")
```

- [ ] **Step 6: Écrire `engine/decodeurs/hex_dec.py`**

```python
import re

PATTERN = re.compile(r"^[0-9a-fA-F]+$")


def detecter(texte):
    t = texte.strip().replace(" ", "")
    if len(t) < 2 or len(t) % 2 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().replace(" ", "")
    brut = bytes.fromhex(t)
    return brut.decode("utf-8", errors="replace")
```

- [ ] **Step 7: Écrire `engine/decodeurs/url_dec.py`**

```python
import re
from urllib.parse import unquote

PATTERN = re.compile(r"%[0-9a-fA-F]{2}")


def detecter(texte):
    occurrences = len(PATTERN.findall(texte))
    if occurrences == 0:
        return 0.0
    return min(0.5 + occurrences * 0.1, 0.9)


def decoder(texte):
    return unquote(texte)
```

- [ ] **Step 8: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_decodeurs_simples.py -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add engine/decodeurs/__init__.py engine/decodeurs/base64_dec.py engine/decodeurs/base32_dec.py engine/decodeurs/hex_dec.py engine/decodeurs/url_dec.py tests/test_decodeurs_simples.py
git commit -m "Ajout des decodeurs base64, base32, hex et url"
```

---

### Task 4 : Décodeurs de substitution (rot13/césar, binaire, morse)

**Files:**
- Create: `engine/decodeurs/rot_dec.py`
- Create: `engine/decodeurs/binaire_dec.py`
- Create: `engine/decodeurs/morse_dec.py`
- Test: `tests/test_decodeurs_substitution.py`

**Interfaces:**
- Consumes: `engine.scoring.score_lisibilite` (défini en tâche 2).
- Produces: `rot_dec.detecter/decoder`, `binaire_dec.detecter/decoder`, `morse_dec.detecter/decoder`.

- [ ] **Step 1: Écrire les tests**

`tests/test_decodeurs_substitution.py` :

```python
from engine.decodeurs import rot_dec, binaire_dec, morse_dec


def test_rot13_retrouve_un_texte_connu():
    # "le chat" decale de 13 -> "yr pung"
    resultat = rot_dec.decoder("yr pung")
    assert resultat.lower() == "le chat"


def test_binaire_round_trip():
    original = "hi"
    encode = " ".join(format(b, "08b") for b in original.encode())

    assert binaire_dec.detecter(encode) > 0.5
    assert binaire_dec.decoder(encode) == original


def test_morse_round_trip():
    encode = "... --- ..."

    assert morse_dec.detecter(encode) > 0.5
    assert morse_dec.decoder(encode) == "sos"
```

- [ ] **Step 2: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_decodeurs_substitution.py -v`
Expected: FAIL (modules manquants)

- [ ] **Step 3: Écrire `engine/decodeurs/rot_dec.py`**

```python
import string

from engine.scoring import score_lisibilite

ALPHABET_MIN = string.ascii_lowercase
ALPHABET_MAJ = string.ascii_uppercase


def _decaler(texte, n):
    resultat = []
    for c in texte:
        if c in ALPHABET_MIN:
            resultat.append(ALPHABET_MIN[(ALPHABET_MIN.index(c) - n) % 26])
        elif c in ALPHABET_MAJ:
            resultat.append(ALPHABET_MAJ[(ALPHABET_MAJ.index(c) - n) % 26])
        else:
            resultat.append(c)
    return "".join(resultat)


def detecter(texte):
    lettres = sum(1 for c in texte if c.isalpha())
    if lettres == 0:
        return 0.0
    return 0.3


def decoder(texte):
    meilleur = texte
    meilleur_score = -1
    for n in range(26):
        candidat = _decaler(texte, n)
        s = score_lisibilite(candidat)
        if s > meilleur_score:
            meilleur_score = s
            meilleur = candidat
    return meilleur
```

- [ ] **Step 4: Écrire `engine/decodeurs/binaire_dec.py`**

```python
import re

PATTERN = re.compile(r"^[01]+$")


def detecter(texte):
    t = texte.strip().replace(" ", "")
    if len(t) < 8 or len(t) % 8 != 0:
        return 0.0
    if not PATTERN.match(t):
        return 0.0
    return 0.6


def decoder(texte):
    t = texte.strip().replace(" ", "")
    octets = [t[i:i + 8] for i in range(0, len(t), 8)]
    brut = bytes(int(o, 2) for o in octets)
    return brut.decode("utf-8", errors="replace")
```

- [ ] **Step 5: Écrire `engine/decodeurs/morse_dec.py`**

```python
TABLE = {
    ".-": "a", "-...": "b", "-.-.": "c", "-..": "d", ".": "e", "..-.": "f",
    "--.": "g", "....": "h", "..": "i", ".---": "j", "-.-": "k", ".-..": "l",
    "--": "m", "-.": "n", "---": "o", ".--.": "p", "--.-": "q", ".-.": "r",
    "...": "s", "-": "t", "..-": "u", "...-": "v", ".--": "w", "-..-": "x",
    "-.--": "y", "--..": "z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9",
}


def detecter(texte):
    t = texte.strip()
    if not t:
        return 0.0
    symboles = set(t) - {" ", "/"}
    if not symboles or not symboles.issubset({".", "-"}):
        return 0.0
    return 0.7


def decoder(texte):
    mots = texte.strip().split("/")
    resultat = []
    for mot in mots:
        lettres = [TABLE.get(code, "") for code in mot.split()]
        resultat.append("".join(lettres))
    return " ".join(resultat)
```

- [ ] **Step 6: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_decodeurs_substitution.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add engine/decodeurs/rot_dec.py engine/decodeurs/binaire_dec.py engine/decodeurs/morse_dec.py tests/test_decodeurs_substitution.py
git commit -m "Ajout des decodeurs rot13/cesar, binaire et morse"
```

---

### Task 5 : Décodeurs web/format (html entities, unicode escape, JWT)

**Files:**
- Create: `engine/decodeurs/html_dec.py`
- Create: `engine/decodeurs/unicode_dec.py`
- Create: `engine/decodeurs/jwt_dec.py`
- Test: `tests/test_decodeurs_web.py`

**Interfaces:**
- Consumes: rien de nouveau.
- Produces: `html_dec.detecter/decoder`, `unicode_dec.detecter/decoder`, `jwt_dec.detecter/decoder`.

- [ ] **Step 1: Écrire les tests**

`tests/test_decodeurs_web.py` :

```python
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
```

- [ ] **Step 2: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_decodeurs_web.py -v`
Expected: FAIL (modules manquants)

- [ ] **Step 3: Écrire `engine/decodeurs/html_dec.py`**

```python
import html
import re

PATTERN = re.compile(r"&[a-zA-Z]+;|&#\d+;")


def detecter(texte):
    if PATTERN.search(texte):
        return 0.7
    return 0.0


def decoder(texte):
    return html.unescape(texte)
```

- [ ] **Step 4: Écrire `engine/decodeurs/unicode_dec.py`**

```python
import re

PATTERN = re.compile(r"\\u[0-9a-fA-F]{4}")


def detecter(texte):
    if PATTERN.search(texte):
        return 0.7
    return 0.0


def decoder(texte):
    return PATTERN.sub(lambda m: chr(int(m.group()[2:], 16)), texte)
```

- [ ] **Step 5: Écrire `engine/decodeurs/jwt_dec.py`**

```python
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
```

- [ ] **Step 6: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_decodeurs_web.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add engine/decodeurs/html_dec.py engine/decodeurs/unicode_dec.py engine/decodeurs/jwt_dec.py tests/test_decodeurs_web.py
git commit -m "Ajout des decodeurs html entities, unicode escape et jwt"
```

---

### Task 6 : Décodeurs avancés (gzip/zlib+base64, xor 1 octet, identification hash)

**Files:**
- Create: `engine/decodeurs/gzip_dec.py`
- Create: `engine/decodeurs/xor_dec.py`
- Create: `engine/decodeurs/hash_dec.py`
- Test: `tests/test_decodeurs_avances.py`

**Interfaces:**
- Consumes: `engine.scoring.score_lisibilite`.
- Produces: `gzip_dec.detecter/decoder`, `xor_dec.detecter/decoder`, `hash_dec.detecter/decoder`.

- [ ] **Step 1: Écrire les tests**

`tests/test_decodeurs_avances.py` :

```python
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
```

- [ ] **Step 2: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_decodeurs_avances.py -v`
Expected: FAIL (modules manquants)

- [ ] **Step 3: Écrire `engine/decodeurs/gzip_dec.py`**

```python
import base64
import gzip
import zlib

ENTETES_ZLIB = (b"\x78\x9c", b"\x78\x01", b"\x78\xda")


def detecter(texte):
    t = texte.strip()
    try:
        brut = base64.b64decode(t, validate=True)
    except Exception:
        return 0.0
    if brut[:2] == b"\x1f\x8b" or brut[:2] in ENTETES_ZLIB:
        return 0.8
    return 0.0


def decoder(texte):
    brut = base64.b64decode(texte.strip())
    try:
        return gzip.decompress(brut).decode("utf-8", errors="replace")
    except OSError:
        return zlib.decompress(brut).decode("utf-8", errors="replace")
```

- [ ] **Step 4: Écrire `engine/decodeurs/xor_dec.py`**

```python
from engine.scoring import score_lisibilite


def _xor(donnees, cle):
    return bytes(b ^ cle for b in donnees)


def detecter(texte):
    if len(texte) < 4:
        return 0.0
    return 0.2


def decoder(texte):
    donnees = texte.encode("latin-1", errors="replace")
    meilleur = texte
    meilleur_score = -1
    for cle in range(256):
        resultat = _xor(donnees, cle)
        try:
            decode = resultat.decode("utf-8")
        except UnicodeDecodeError:
            continue
        s = score_lisibilite(decode)
        if s > meilleur_score:
            meilleur_score = s
            meilleur = decode
    return meilleur
```

- [ ] **Step 5: Écrire `engine/decodeurs/hash_dec.py`**

```python
import re

LONGUEURS = {32: "MD5", 40: "SHA1", 64: "SHA256"}


def detecter(texte):
    t = texte.strip()
    if len(t) in LONGUEURS and re.fullmatch(r"[0-9a-fA-F]+", t):
        return 0.5
    return 0.0


def decoder(texte):
    t = texte.strip()
    nom = LONGUEURS.get(len(t), "hash")
    return f"[{nom} detecte, non reversible] {t}"
```

- [ ] **Step 6: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_decodeurs_avances.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add engine/decodeurs/gzip_dec.py engine/decodeurs/xor_dec.py engine/decodeurs/hash_dec.py tests/test_decodeurs_avances.py
git commit -m "Ajout des decodeurs gzip, xor et identification de hash"
```

---

### Task 7 : Registre des décodeurs et moteur récursif

**Files:**
- Modify: `engine/decodeurs/__init__.py`
- Create: `engine/recursive.py`
- Test: `tests/test_recursive.py`

**Interfaces:**
- Consumes: tous les modules `engine/decodeurs/*.py` (tâches 3-6), `Candidat` (tâche 2), `score_lisibilite` (tâche 2).
- Produces: `TOUS` (liste de tuples `(nom: str, module)`), `detect_layer(texte: str) -> list[Candidat]`, `auto_decode(texte: str, profondeur_max: int = 10) -> Candidat`.

- [ ] **Step 1: Écrire les tests**

`tests/test_recursive.py` :

```python
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
```

- [ ] **Step 2: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_recursive.py -v`
Expected: FAIL (`engine.recursive` n'existe pas)

- [ ] **Step 3: Remplir `engine/decodeurs/__init__.py`**

```python
from . import (
    base64_dec,
    base32_dec,
    hex_dec,
    url_dec,
    rot_dec,
    binaire_dec,
    morse_dec,
    html_dec,
    unicode_dec,
    jwt_dec,
    gzip_dec,
    xor_dec,
    hash_dec,
)

TOUS = [
    ("base64", base64_dec),
    ("base32", base32_dec),
    ("hex", hex_dec),
    ("url", url_dec),
    ("rot13_cesar", rot_dec),
    ("binaire", binaire_dec),
    ("morse", morse_dec),
    ("html", html_dec),
    ("unicode", unicode_dec),
    ("jwt", jwt_dec),
    ("gzip", gzip_dec),
    ("xor", xor_dec),
    ("hash", hash_dec),
]
```

- [ ] **Step 4: Écrire `engine/recursive.py`**

```python
from engine.decodeurs import TOUS
from engine.scoring import score_lisibilite
from engine.types import Candidat

SEUIL_DETECTION = 0.5
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
```

- [ ] **Step 5: Lancer les tests, vérifier qu'ils passent**

Run: `pytest tests/test_recursive.py -v`
Expected: PASS

- [ ] **Step 6: Lancer toute la suite de tests**

Run: `pytest -v`
Expected: PASS (tous les tests des tâches 2 à 7)

- [ ] **Step 7: Commit**

```bash
git add engine/decodeurs/__init__.py engine/recursive.py tests/test_recursive.py
git commit -m "Ajout du registre des decodeurs et du moteur recursif"
```

---

### Task 8 : CLI

**Files:**
- Create: `cli/__main__.py`

**Interfaces:**
- Consumes: `engine.recursive.auto_decode` (tâche 7).
- Produces: exécutable via `python -m cli "<texte>"` depuis la racine du dépôt.

- [ ] **Step 1: Écrire `cli/__main__.py`**

```python
import sys

from engine.recursive import auto_decode


def afficher(noeud, indent=0):
    prefixe = "  " * indent
    print(f"{prefixe}[{noeud.decodeur}] (lisibilite={noeud.score_lisibilite:.2f}) {noeud.texte!r}")
    for enfant in noeud.enfants:
        afficher(enfant, indent + 1)


def main():
    if len(sys.argv) < 2:
        print('Usage: python -m cli "texte a decoder"')
        sys.exit(1)
    texte = sys.argv[1]
    arbre = auto_decode(texte)
    afficher(arbre)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Tester manuellement**

Run: `python -m cli "$(python3 -c "import base64; print(base64.b64encode(b'bonjour').decode())")"`
Expected: la sortie affiche la couche `entree`, puis une couche `base64` avec le texte `'bonjour'`.

- [ ] **Step 3: Commit**

```bash
git add cli/__main__.py
git commit -m "Ajout de la CLI"
```

---

### Task 9 : API FastAPI

**Files:**
- Create: `api/main.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `engine.recursive.auto_decode`, `engine.recursive.detect_layer`, `engine.decodeurs.TOUS` (tâche 7).
- Produces: endpoints `POST /decode`, `POST /decode/step`, `GET /decodeurs`.

- [ ] **Step 1: Ajouter `httpx` à `requirements.txt` (nécessaire au client de test FastAPI)**

Modifier `requirements.txt` :

```
fastapi
uvicorn[standard]
pytest
httpx
```

- [ ] **Step 2: Écrire les tests**

`tests/test_api.py` :

```python
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
```

- [ ] **Step 3: Lancer les tests, vérifier qu'ils échouent**

Run: `pytest tests/test_api.py -v`
Expected: FAIL (`api.main` n'existe pas)

- [ ] **Step 4: Écrire `api/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.decodeurs import TOUS
from engine.recursive import auto_decode, detect_layer

app = FastAPI(title="RRF OG LOCK")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequeteDecode(BaseModel):
    texte: str
    profondeur_max: int = 10


class RequeteEtape(BaseModel):
    texte: str


def _serialiser(noeud):
    return {
        "decodeur": noeud.decodeur,
        "score_detection": noeud.score_detection,
        "texte": noeud.texte,
        "score_lisibilite": noeud.score_lisibilite,
        "enfants": [_serialiser(e) for e in noeud.enfants],
    }


@app.post("/decode")
def decoder_auto(requete: RequeteDecode):
    arbre = auto_decode(requete.texte, requete.profondeur_max)
    return _serialiser(arbre)


@app.post("/decode/step")
def decoder_etape(requete: RequeteEtape):
    candidats = detect_layer(requete.texte)
    return [
        {
            "decodeur": c.decodeur,
            "score_detection": c.score_detection,
            "texte": c.texte,
            "score_lisibilite": c.score_lisibilite,
        }
        for c in candidats
    ]


@app.get("/decodeurs")
def liste_decodeurs():
    return [nom for nom, _ in TOUS]
```

- [ ] **Step 5: Lancer les tests, vérifier qu'ils passent**

Run: `pip install -r requirements.txt && pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add requirements.txt api/main.py tests/test_api.py
git commit -m "Ajout de l'API FastAPI"
```

---

### Task 10 : Front React

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/App.css`
- Create: `frontend/src/api.js`

**Interfaces:**
- Consumes: `POST /decode`, `POST /decode/step`, `GET /decodeurs` (tâche 9), via proxy Vite vers `http://localhost:8000`.
- Produces: interface web accessible via `npm run dev` dans `frontend/`.

- [ ] **Step 1: Écrire `frontend/package.json`**

```json
{
  "name": "rrf-og-lock-front",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Écrire `frontend/vite.config.js`**

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/decode": "http://localhost:8000",
      "/decodeurs": "http://localhost:8000",
    },
  },
});
```

- [ ] **Step 3: Écrire `frontend/index.html`**

```html
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <title>RRF OG LOCK</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Écrire `frontend/src/api.js`**

```javascript
export async function decoderAuto(texte, profondeurMax = 10) {
  const reponse = await fetch("/decode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texte, profondeur_max: profondeurMax }),
  });
  return reponse.json();
}

export async function decoderEtape(texte) {
  const reponse = await fetch("/decode/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texte }),
  });
  return reponse.json();
}
```

- [ ] **Step 5: Écrire `frontend/src/App.jsx`**

```jsx
import { useState } from "react";
import { decoderAuto, decoderEtape } from "./api.js";

function Noeud({ noeud }) {
  return (
    <li>
      <span className="decodeur">{noeud.decodeur}</span>
      <span className="score">lisibilite {noeud.score_lisibilite.toFixed(2)}</span>
      <pre>{noeud.texte}</pre>
      {noeud.enfants.length > 0 && (
        <ul>
          {noeud.enfants.map((enfant, i) => (
            <Noeud key={i} noeud={enfant} />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function App() {
  const [texte, setTexte] = useState("");
  const [arbre, setArbre] = useState(null);
  const [modePasAPas, setModePasAPas] = useState(false);
  const [etapes, setEtapes] = useState([]);
  const [texteCourant, setTexteCourant] = useState("");
  const [candidatsCourants, setCandidatsCourants] = useState([]);

  async function lancerAuto() {
    const resultat = await decoderAuto(texte);
    setArbre(resultat);
  }

  async function demarrerPasAPas() {
    setTexteCourant(texte);
    setEtapes([]);
    const candidats = await decoderEtape(texte);
    setCandidatsCourants(candidats);
  }

  async function choisirCandidat(candidat) {
    setEtapes([...etapes, candidat]);
    setTexteCourant(candidat.texte);
    const candidats = await decoderEtape(candidat.texte);
    setCandidatsCourants(candidats);
  }

  function basculerModePasAPas() {
    const nouveauMode = !modePasAPas;
    setModePasAPas(nouveauMode);
    if (nouveauMode) demarrerPasAPas();
  }

  return (
    <div className="app">
      <h1>RRF OG LOCK</h1>
      <textarea
        value={texte}
        onChange={(e) => setTexte(e.target.value)}
        placeholder="Colle ta chaine encodee ici"
      />
      <div className="boutons">
        <button onClick={lancerAuto}>Decoder (auto)</button>
        <button onClick={basculerModePasAPas}>
          {modePasAPas ? "Quitter le mode pas-a-pas" : "Mode pas-a-pas"}
        </button>
      </div>

      {!modePasAPas && arbre && (
        <ul className="resultat">
          <Noeud noeud={arbre} />
        </ul>
      )}

      {modePasAPas && (
        <div className="pas-a-pas">
          <h2>Texte courant</h2>
          <pre>{texteCourant}</pre>

          <h2>Couches detectees</h2>
          <ul>
            {candidatsCourants.map((c, i) => (
              <li key={i}>
                <button onClick={() => choisirCandidat(c)}>
                  {c.decodeur} (score {c.score_detection.toFixed(2)}) -&gt; {c.texte.slice(0, 40)}
                </button>
              </li>
            ))}
          </ul>

          <h2>Historique</h2>
          <ol>
            {etapes.map((e, i) => (
              <li key={i}>{e.decodeur}: {e.texte.slice(0, 60)}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Écrire `frontend/src/main.jsx`**

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 7: Écrire `frontend/src/App.css`**

```css
body {
  margin: 0;
  font-family: sans-serif;
  background: #1a1a1a;
  color: #f5f5f5;
}

.app {
  max-width: 700px;
  margin: 40px auto;
  padding: 0 20px;
}

textarea {
  width: 100%;
  height: 100px;
  font-family: monospace;
}

.boutons {
  margin: 10px 0;
}

.boutons button {
  margin-right: 8px;
}

.resultat ul {
  list-style: none;
  padding-left: 20px;
  border-left: 2px solid #555;
}

.decodeur {
  font-weight: bold;
  margin-right: 8px;
}

.score {
  color: #999;
  font-size: 0.85em;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
  background: #262626;
  padding: 6px;
  border-radius: 4px;
}
```

- [ ] **Step 8: Tester manuellement**

Run (dans un terminal) : `uvicorn api.main:app --reload` depuis la racine.
Run (dans un second terminal) : `cd frontend && npm install && npm run dev`
Ouvrir l'URL affichée par Vite, coller une chaîne encodée en base64 (ex. `Ym9uam91cg==`), cliquer sur "Decoder (auto)".
Expected : la timeline affiche la couche `entree` puis `base64` avec le texte `bonjour`. Tester aussi le bouton "Mode pas-a-pas".

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "Ajout du front React"
```

---

### Task 11 : README et vérification finale

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: rien (documentation).

- [ ] **Step 1: Écrire `README.md`**

```markdown
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
```

- [ ] **Step 2: Lancer toute la suite de tests une dernière fois**

Run: `pytest -v`
Expected: PASS (tous les tests, toutes tâches confondues)

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Ajout du README"
```
