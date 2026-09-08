import { useEffect, useState } from "react";
import { decoderAuto, decoderEtape, listerDecodeurs } from "./api.js";

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

function meilleureFeuille(noeud) {
  if (!noeud.enfants || noeud.enfants.length === 0) return noeud;
  return noeud.enfants
    .map(meilleureFeuille)
    .reduce((a, b) => (b.score_lisibilite > a.score_lisibilite ? b : a));
}

export default function App() {
  const [texte, setTexte] = useState("");
  const [arbre, setArbre] = useState(null);
  const [modePasAPas, setModePasAPas] = useState(false);
  const [etapes, setEtapes] = useState([]);
  const [texteCourant, setTexteCourant] = useState("");
  const [candidatsCourants, setCandidatsCourants] = useState([]);
  const [decodeurs, setDecodeurs] = useState([]);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    listerDecodeurs().then(setDecodeurs).catch(() => {});
  }, []);

  async function lancerAuto() {
    setChargement(true);
    setErreur("");
    try {
      const resultat = await decoderAuto(texte);
      setArbre(resultat);
    } catch (e) {
      setErreur("Echec du decodage : " + e.message);
    } finally {
      setChargement(false);
    }
  }

  async function demarrerPasAPas() {
    setChargement(true);
    setErreur("");
    try {
      setTexteCourant(texte);
      setEtapes([]);
      const candidats = await decoderEtape(texte);
      setCandidatsCourants(candidats);
    } catch (e) {
      setErreur("Echec du decodage : " + e.message);
    } finally {
      setChargement(false);
    }
  }

  async function choisirCandidat(candidat) {
    setChargement(true);
    setErreur("");
    try {
      setEtapes([...etapes, candidat]);
      setTexteCourant(candidat.texte);
      const candidats = await decoderEtape(candidat.texte);
      setCandidatsCourants(candidats);
    } catch (e) {
      setErreur("Echec du decodage : " + e.message);
    } finally {
      setChargement(false);
    }
  }

  function basculerModePasAPas() {
    const nouveauMode = !modePasAPas;
    setModePasAPas(nouveauMode);
    if (nouveauMode) demarrerPasAPas();
  }

  return (
    <div className="app">
      <h1>RRF OG LOCK</h1>
      {decodeurs.length > 0 && (
        <p className="decodeurs-dispo">Decodeurs disponibles : {decodeurs.join(", ")}</p>
      )}
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

      {chargement && <p className="chargement">Decodage en cours...</p>}
      {erreur && <p className="erreur">{erreur}</p>}

      {!modePasAPas && arbre && (
        <>
          <div className="meilleur-resultat">
            <h2>Meilleur resultat</h2>
            <pre>{meilleureFeuille(arbre).texte}</pre>
            <span className="score">
              lisibilite {meilleureFeuille(arbre).score_lisibilite.toFixed(2)}
            </span>
          </div>
          <ul className="resultat">
            <Noeud noeud={arbre} />
          </ul>
        </>
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
