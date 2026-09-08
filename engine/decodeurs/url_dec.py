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
