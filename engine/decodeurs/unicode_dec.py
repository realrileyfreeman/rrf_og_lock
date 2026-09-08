import re

PATTERN = re.compile(r"\\u[0-9a-fA-F]{4}")


def detecter(texte):
    if PATTERN.search(texte):
        return 0.7
    return 0.0


def decoder(texte):
    return PATTERN.sub(lambda m: chr(int(m.group()[2:], 16)), texte)
