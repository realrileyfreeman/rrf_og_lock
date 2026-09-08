# RRF OG LOCK — Design

## Contexte

Projet réalisé dans le cadre d'un master : un outil de décodage automatique et récursif
de chaînes de caractères encodées sur plusieurs couches (ex: Base64 d'un Hex d'un ROT13).
Le nom du projet référence Boondocks (choix esthétique pour le front).

## Objectif

Étant donné une chaîne de texte, détecter automatiquement quel(s) encodage(s) elle utilise,
la décoder, puis répéter récursivement sur le résultat jusqu'à obtenir du texte clair
(ou une limite de profondeur), sans que l'utilisateur ait à préciser les couches à l'avance.

## Non-objectifs

- Pas de cassage de chiffrement fort (AES avec clé inconnue, etc.) — hors scope.
- Pas de comptes utilisateurs, pas de persistance serveur (stateless).
- Pas de vérification de signature JWT — décodage informatif du header/payload uniquement.

## Architecture

Mono-repo, un seul cœur de logique (`engine/`) partagé par l'API, le CLI et les tests —
pour ne jamais dupliquer l'algorithme de décodage entre les façades.

```
rrf_og_lock/
├── engine/          # moteur de décodage, pure Python, zéro dépendance web
│   ├── decoders/    # un module par encodage (base64.py, hex.py, rot.py, ...)
│   ├── scoring.py   # heuristique "texte lisible"
│   └── recursive.py # orchestration récursive (auto + pas-à-pas)
├── api/             # FastAPI, expose engine/ en HTTP
├── cli/             # wrapper CLI (argparse) autour de engine/
├── frontend/        # React + Vite
└── tests/           # pytest
```

## Le moteur (`engine/`)

### Interface d'un décodeur

Chaque encodage est un module exposant :
- `detect(text: str) -> float` — score de confiance 0.0-1.0 que `text` utilise cet encodage
  (regex/alphabet valide, longueur, ratio de caractères, etc.)
- `decode(text: str) -> str` — décode `text` en supposant qu'il utilise cet encodage.

Décodeurs de la V1 :
- Base64 (standard + urlsafe)
- Base32
- Hex (Base16)
- URL encoding (`%XX`)
- ROT13 / César (bruteforce des 25 rotations, garde la meilleure)
- Binaire (suites de 0/1)
- Morse
- HTML entities (`&amp;`, `&#39;`, ...)
- Unicode escapes (`\uXXXX`)
- Gzip/zlib compressé + Base64
- JWT (décodage header/payload base64url, sans vérif de signature)
- XOR à clé courte (bruteforce clés 1 à 4 octets, garde le résultat le plus "lisible")
- Identification de hash (MD5/SHA1/SHA256 par longueur+alphabet hex) — détection seule,
  pas de décodage (irréversible), signalé comme tel dans le résultat.

### Algorithme récursif

À chaque couche :
1. Faire tourner tous les `detect()` sur le texte courant.
2. Garder les candidats dont le score dépasse un seuil (défaut 0.5).
3. Décoder chaque candidat retenu.
4. Scorer chaque résultat obtenu avec l'heuristique "texte lisible" (ratio de caractères
   ASCII imprimables + reconnaissance de mots courants FR/EN via une petite liste de
   stopwords, pas de dépendance NLP lourde).
5. Continuer récursivement sur les 2-3 meilleurs résultats (pas 1 seul, pas tous — limite
   la combinatoire tout en couvrant les cas ambigus comme "ressemble à du Hex ET à du Base64").

Arrêt d'une branche quand : le score "texte lisible" dépasse un seuil (défaut 0.8), OU
profondeur max atteinte (défaut 10, paramétrable), OU aucun décodeur ne matche.

Le moteur retourne un **arbre** (pas juste la meilleure branche), pour permettre au front
d'afficher tout le chemin exploré et les branches alternatives.

### Deux modes d'utilisation

- `auto_decode(text, max_depth=10) -> DecodeTree` : explore tout l'arbre directement, mode
  par défaut.
- `detect_layer(text) -> list[Candidate]` : ne traite qu'une seule couche, retourne les
  candidats scorés ; utilisé par le mode pas-à-pas pour laisser l'utilisateur choisir la
  branche à suivre avant de continuer.

## API (FastAPI)

- `POST /decode` — body `{text: str, max_depth?: int}` → `DecodeTree` complet (mode auto).
- `POST /decode/step` — body `{text: str}` → `list[Candidate]` (une couche, mode pas-à-pas).
- `GET /decoders` — liste des décodeurs disponibles (pour affichage front).
- Pas de DB, pas d'auth. CORS ouvert en dev.

## Front (React + Vite)

- Zone de saisie + bouton "Décoder" (mode auto par défaut).
- Résultat affiché en timeline verticale des couches (couche détectée → texte obtenu),
  résultat final mis en évidence.
- Bascule vers le mode pas-à-pas : affiche les candidats scorés de la couche courante,
  l'utilisateur clique celui à suivre.
- Thème visuel : police et palette inspirées de Boondocks (asset image à intégrer une fois
  fournie par l'utilisateur).

## CLI

`python -m rrf_og_lock "<texte>"` → appelle `engine.auto_decode` directement (pas de
dépendance à l'API), imprime l'arbre en texte dans le terminal.

## Tests

pytest dans `tests/` :
- Un test round-trip par décodeur (encode puis `detect`/`decode` retrouve l'original).
- Quelques tests d'intégration multicouche (ex: texte encodé Base64→Hex→ROT13, vérifier
  que `auto_decode` retrouve le texte clair).

## Repo GitHub

- README avec contexte master, instructions d'installation/lancement
  (`uvicorn api.main:app`, `npm run dev` dans `frontend/`, CLI).
- Licence MIT.
- `.gitignore` Python + Node standard.
