async function verifier(reponse) {
  if (!reponse.ok) {
    throw new Error(`Erreur serveur (${reponse.status})`);
  }
  return reponse.json();
}

export async function decoderAuto(texte, profondeurMax = 10) {
  const reponse = await fetch("/decode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texte, profondeur_max: profondeurMax }),
  });
  return verifier(reponse);
}

export async function decoderEtape(texte) {
  const reponse = await fetch("/decode/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texte }),
  });
  return verifier(reponse);
}

export async function listerDecodeurs() {
  const reponse = await fetch("/decodeurs");
  return verifier(reponse);
}
