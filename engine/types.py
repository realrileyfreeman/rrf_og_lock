from dataclasses import dataclass, field


@dataclass
class Candidat:
    decodeur: str
    score_detection: float
    texte: str
    score_lisibilite: float
    enfants: list["Candidat"] = field(default_factory=list)
