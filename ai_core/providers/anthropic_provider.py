"""Fournisseur Claude via l'API Anthropic."""

import json
import os

from ..validation import to_strict_schema
from .base import AIResponse


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
        self, system: str, user: str, model: str, max_tokens: int, output_schema: dict | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        kwargs = {}
        if output_schema:
            # Sortie structurée native ("structured outputs") : la réponse est directement un JSON
            # contraint par le schéma. Contrairement au détournement d'un outil (tool use), le modèle
            # n'utilise pas sa syntaxe interne d'appel d'outil, qui fuyait parfois dans les textes.
            kwargs["output_config"] = {
                "format": {"type": "json_schema", "schema": to_strict_schema(output_schema)}
            }

        if temperature is not None:
            # 0 = réponses les plus stables d'une exécution à l'autre (utile pour une évaluation)
            kwargs["temperature"] = temperature

        msg = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            **kwargs,
        )
        text = "".join(block.text for block in msg.content if block.type == "text")

        data = None
        if output_schema:
            if msg.stop_reason == "max_tokens":
                # On montre la fin de la réponse (déjà masquée) pour comprendre ce qui a débordé
                raise RuntimeError(
                    f"Réponse tronquée après {msg.usage.output_tokens} tokens (max_tokens={max_tokens}). "
                    f"Fin de la réponse : ...{text[-300:]!r}"
                )
            data = json.loads(text)

        return AIResponse(
            text=text,
            model=msg.model,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            data=data,
        )
