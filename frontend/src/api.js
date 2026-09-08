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
