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
