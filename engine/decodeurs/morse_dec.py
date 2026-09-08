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
