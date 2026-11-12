"""Fournisseur Claude via l'API Anthropic."""

import json
import os

from .base import AIResponse

# Nom de l'outil "virtuel" que Claude est obligé d'appeler pour rendre une réponse structurée
STRUCTURED_TOOL = "rendre_resultat"


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None):
        # Import ici pour que les tests n'aient pas besoin du SDK installé
        import anthropic

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY absente. En CI, la définir dans les Secrets du dépôt."
            )
        self._client = anthropic.Anthropic(api_key=key)

    def complete(
        self, system: str, user: str, model: str, max_tokens: int, output_schema: dict | None = None
    ) -> AIResponse:
        kwargs = {}
        if output_schema:
            # Sortie structurée : on force l'appel d'un outil dont le schéma d'entrée est le format attendu.
            # L'API garantit alors un JSON valide, sans souci de guillemets ou de texte parasite.
            kwargs["tools"] = [{
                "name": STRUCTURED_TOOL,
                "description": "Transmet le résultat final de l'analyse.",
                "input_schema": output_schema,
            }]
            kwargs["tool_choice"] = {"type": "tool", "name": STRUCTURED_TOOL}

        msg = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            **kwargs,
        )

        data = None
        text_parts = []
        for block in msg.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use" and block.name == STRUCTURED_TOOL:
                data = dict(block.input)

        if output_schema and data is None:
            raise RuntimeError(f"Réponse structurée absente (stop_reason={msg.stop_reason})")

        return AIResponse(
            text=json.dumps(data, ensure_ascii=False) if data is not None else "".join(text_parts),
            model=msg.model,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            data=data,
        )
