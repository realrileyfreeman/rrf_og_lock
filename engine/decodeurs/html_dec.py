import html
import re

PATTERN = re.compile(r"&[a-zA-Z]+;|&#\d+;")


def detecter(texte):
    if PATTERN.search(texte):
        return 0.7
    return 0.0


def decoder(texte):
    return html.unescape(texte)
