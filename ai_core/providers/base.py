"""Contrat commun à tous les fournisseurs d'IA.

Le reste du projet ne parle qu'à cette interface. Pour changer de modèle
ou de fournisseur (Bedrock, Vertex AI, Azure, modèle interne...), il suffit
d'ajouter une classe qui respecte ce contrat.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class AIResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class AIProvider(Protocol):
    name: str

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> AIResponse:
        """Envoie un prompt et renvoie la réponse texte du modèle."""
        ...
