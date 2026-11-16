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
    # Réponse structurée, remplie quand un schéma de sortie est demandé
    data: dict | None = None


class AIProvider(Protocol):
    name: str

    def complete(
        self, system: str, user: str, model: str, max_tokens: int, output_schema: dict | None = None
    ) -> AIResponse:
        """Envoie un prompt. Avec output_schema, la réponse doit respecter ce schéma JSON (dans .data)."""
        ...
