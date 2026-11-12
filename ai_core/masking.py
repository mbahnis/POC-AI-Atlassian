"""Masquage des données sensibles avant envoi au modèle.

Approche volontairement simple (expressions régulières) pour le POC.
En production, on peut brancher un outil dédié (ex. Microsoft Presidio)
ou des règles propres au client, sans toucher au reste du code.
"""

import re

# L'ordre compte : les motifs les plus spécifiques d'abord.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("SECRET", re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})\b")),
    ("IBAN", re.compile(r"\bFR\d{2}(?: ?[A-Z0-9]{4}){5}(?: ?[A-Z0-9]{1,3})?\b")),
    ("CARTE", re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("TELEPHONE", re.compile(r"(?<!\d)(?:\+33 ?|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)")),
    ("IP", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]


def mask(text: str) -> tuple[str, dict[str, int]]:
    """Remplace les données sensibles par des balises [EMAIL], [IP]...

    Retourne le texte masqué et le nombre de remplacements par type,
    ce qui alimente le journal d'audit sans jamais y écrire la donnée.
    """
    counts: dict[str, int] = {}
    for label, pattern in PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts
